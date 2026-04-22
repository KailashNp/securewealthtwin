// ─────────────────────────────────────────────────────────────────
// routes/action.js – 3-step Fraud Intercept Pipeline
//
//  POST /api/action/execute
//  1. Call Fraud Engine → evaluate risk score
//  2. ALLOW  → call Wealth Engine to validate & execute, return success
//  3. WARN   → return warning + 30s cooldown payload
//  4. BLOCK  → write to audit log, return block payload
// ─────────────────────────────────────────────────────────────────

const express = require('express');
const axios = require('axios');
const { verifyToken } = require('../middleware/auth');
const { writeAuditLog, getAuditLog } = require('../utils/auditLog');
const router = express.Router();

const WEALTH_URL = process.env.WEALTH_ENGINE_URL || 'http://localhost:8001';
const FRAUD_URL  = process.env.FRAUD_ENGINE_URL  || 'http://localhost:8002';

/**
 * POST /api/action/execute
 * Body: {
 *   userId, action_type, amount, fund_or_product,
 *   device_id, otp_attempts
 * }
 *
 * This is the most critical endpoint — it orchestrates the full
 * fraud intercept flow before any financial action is processed.
 */
router.post('/execute', verifyToken, async (req, res) => {
  const { userId, action_type, amount, fund_or_product, device_id, otp_attempts } = req.body;

  if (!userId || !action_type || !amount) {
    return res.status(400).json({ error: 'userId, action_type, and amount are required' });
  }

  console.log(`[Action] Executing ${action_type} for user ${userId} — amount: ₹${amount}`);

  // ── Step 1: Call Fraud Engine ─────────────────────────────────
  let fraudResult;
  try {
    const fraudResponse = await axios.post(`${FRAUD_URL}/api/risk/evaluate`, {
      user_id: userId,
      action_type,
      amount,
      fund_or_product: fund_or_product || '',
      device_id: device_id || 'unknown',
      otp_attempts: otp_attempts || 1,
      is_trusted_device: req.user.isTrustedDevice,
    }, { timeout: 5000 });

    fraudResult = fraudResponse.data;
    console.log(`[Action] Fraud Engine decision: ${fraudResult.decision} (score: ${fraudResult.risk_score})`);
  } catch (err) {
    // Fraud Engine down — fall back to stub evaluation
    console.warn('[Action] Fraud Engine unreachable — using stub evaluation');
    fraudResult = stubFraudEvaluate({ userId, action_type, amount, device_id, otp_attempts, isTrustedDevice: req.user.isTrustedDevice });
  }

  const actionId = `act_${Date.now()}_${userId}`;

  // ── Step 2: ALLOW → validate with Wealth Engine ──────────────
  if (fraudResult.decision === 'allow') {
    let wealthResult = { status: 'simulated', message: 'Action queued in Wealth Engine' };

    try {
      const wealthResponse = await axios.post(`${WEALTH_URL}/actions/confirm`, {
        action_id: actionId,
        user_id: userId,
        action_type,
        amount,
        fund_or_product,
      }, { timeout: 5000 });
      wealthResult = wealthResponse.data;
    } catch (err) {
      console.warn('[Action] Wealth Engine unreachable — simulating execution');
    }

    writeAuditLog({ actionId, userId, action_type, amount, decision: 'allow', risk_score: fraudResult.risk_score, timestamp: new Date().toISOString() });

    return res.json({
      action_id: actionId,
      decision: 'allow',
      risk_score: fraudResult.risk_score,
      risk_level: fraudResult.risk_level,
      message: fraudResult.message || 'Action approved. Proceeding with execution.',
      signals: fraudResult.signals || {},
      wealth_result: wealthResult,
    });
  }

  // ── Step 3: WARN → return warning + cooldown ─────────────────
  if (fraudResult.decision === 'warn') {
    writeAuditLog({ actionId, userId, action_type, amount, decision: 'warn', risk_score: fraudResult.risk_score, timestamp: new Date().toISOString() });

    return res.status(200).json({
      action_id: actionId,
      decision: 'warn',
      risk_score: fraudResult.risk_score,
      risk_level: fraudResult.risk_level,
      message: fraudResult.message || 'Unusual activity detected. Please confirm after 30 seconds.',
      signals: fraudResult.signals || {},
      cooldown_seconds: 30,
    });
  }

  // ── Step 4: BLOCK → audit log + block payload ─────────────────
  writeAuditLog({ actionId, userId, action_type, amount, decision: 'block', risk_score: fraudResult.risk_score, timestamp: new Date().toISOString(), reason: fraudResult.message });
  console.warn(`[Action] BLOCKED action ${actionId} for user ${userId}. Score: ${fraudResult.risk_score}`);

  return res.status(200).json({
    action_id: actionId,
    decision: 'block',
    risk_score: fraudResult.risk_score,
    risk_level: 'high',
    message: fraudResult.message || 'This action has been blocked due to high fraud risk.',
    signals: fraudResult.signals || {},
  });
});

/**
 * POST /api/action/confirm
 * Confirms a previously warned action (after cooldown).
 */
router.post('/confirm', verifyToken, async (req, res) => {
  const { action_id } = req.body;
  if (!action_id) return res.status(400).json({ error: 'action_id is required' });

  writeAuditLog({ actionId: action_id, decision: 'confirmed_after_warn', timestamp: new Date().toISOString() });

  return res.json({ action_id, status: 'confirmed', message: 'Action confirmed and executed (simulated).' });
});

/**
 * GET /api/action/audit-log
 * Returns all logged actions for transparency.
 */
router.get('/audit-log', verifyToken, (req, res) => {
  const { userId } = req.query;
  const log = getAuditLog(userId ? Number(userId) : null);
  res.json({ total: log.length, entries: log });
});

// ── Stub Fraud Evaluation (used when Fraud Engine is down) ────────
function stubFraudEvaluate({ userId, action_type, amount, device_id, otp_attempts, isTrustedDevice }) {
  let score = 0;
  const signals = {};

  if (!isTrustedDevice) {
    score += 20;
    signals.untrusted_device = { points: 20, triggered: true, detail: 'Login from unrecognized device' };
  }
  if (otp_attempts >= 3) {
    score += 25;
    signals.otp_abuse = { points: 25, triggered: true, detail: `${otp_attempts} OTP attempts detected` };
  }
  if (amount >= 500000) {
    score += 30;
    signals.large_amount = { points: 30, triggered: true, detail: `Amount ₹${amount.toLocaleString()} exceeds threshold` };
  }
  if (['large_transfer', 'redeem'].includes(action_type)) {
    score += 15;
    signals.high_risk_action = { points: 15, triggered: true, detail: `Action type "${action_type}" is high-risk` };
  }

  let decision, risk_level, message;
  if (score < 30)       { decision = 'allow'; risk_level = 'low';    message = 'Action approved. All checks passed.'; }
  else if (score < 60)  { decision = 'warn';  risk_level = 'medium'; message = 'Elevated risk detected. Please confirm after 30 seconds.'; }
  else                  { decision = 'block'; risk_level = 'high';   message = 'Action blocked. Multiple fraud signals triggered.'; }

  return { decision, risk_level, risk_score: score, message, signals, _stub: true };
}

module.exports = router;
