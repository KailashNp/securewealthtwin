// ─────────────────────────────────────────────────────────────────
// routes/user.js – User profile & portfolio stubs
// Proxies to Wealth Engine; returns stubs when service is down.
// ─────────────────────────────────────────────────────────────────

const express = require('express');
const axios = require('axios');
const { verifyToken } = require('../middleware/auth');
const router = express.Router();

const WEALTH_URL = process.env.WEALTH_ENGINE_URL || 'http://localhost:8001';

// Stub profiles — replaced by real Wealth Engine call once it's up
const STUB_PROFILES = {
  1: { id: 1, name: 'Arjun Mehta',   health_score: 78, savings_rate: 0.22, risk_appetite: 'moderate', kyc_verified: true,  monthly_income: 120000 },
  2: { id: 2, name: 'Priya Sharma',  health_score: 85, savings_rate: 0.30, risk_appetite: 'conservative', kyc_verified: true, monthly_income: 95000  },
  3: { id: 3, name: 'Ravi Kumar',    health_score: 62, savings_rate: 0.12, risk_appetite: 'aggressive', kyc_verified: false, monthly_income: 150000 },
  4: { id: 4, name: 'Fatima Sheikh', health_score: 91, savings_rate: 0.35, risk_appetite: 'conservative', kyc_verified: true, monthly_income: 80000  },
};

/**
 * GET /api/user/:id/profile
 * Returns user profile + financial health score.
 * Tries Wealth Engine first, falls back to stub.
 */
router.get('/:id/profile', verifyToken, async (req, res) => {
  const userId = Number(req.params.id);

  try {
    const response = await axios.get(`${WEALTH_URL}/users/${userId}`, { timeout: 3000 });
    return res.json(response.data);
  } catch (err) {
    console.warn(`[User] Wealth Engine unreachable — returning stub for user ${userId}`);
    const stub = STUB_PROFILES[userId];
    if (!stub) return res.status(404).json({ error: 'User not found' });
    return res.json({ ...stub, _stub: true });
  }
});

/**
 * GET /api/user/:id/dashboard
 * Returns full dashboard data: net worth, assets, spending, goals.
 */
router.get('/:id/dashboard', verifyToken, async (req, res) => {
  const userId = Number(req.params.id);

  try {
    const response = await axios.get(`${WEALTH_URL}/dashboard/${userId}`, { timeout: 3000 });
    return res.json(response.data);
  } catch (err) {
    console.warn(`[User] Wealth Engine unreachable — returning stub dashboard for user ${userId}`);
    return res.json({
      _stub: true,
      user: STUB_PROFILES[userId] || { id: userId, name: 'Unknown' },
      net_worth: 1250000,
      total_assets: 1850000,
      spending_summary: {
        monthly_income: 120000,
        total_expense: 93600,
        savings_rate: 22,
        category_breakdown: { rent: 30000, groceries: 12000, utilities: 5000, dining: 8000, investment: 15000, other: 23600 },
        monthly_trend: [],
      },
      goals: [],
    });
  }
});

/**
 * GET /api/user/:id/assets
 * Returns portfolio of assets.
 */
router.get('/:id/assets', verifyToken, async (req, res) => {
  const userId = Number(req.params.id);

  try {
    const response = await axios.get(`${WEALTH_URL}/assets/`, { params: { user_id: userId }, timeout: 3000 });
    return res.json(response.data);
  } catch (err) {
    console.warn(`[User] Wealth Engine unreachable — returning stub assets`);
    return res.json([
      { id: 1, name: 'Index Fund SIP',    asset_type: 'MUTUAL_FUND', current_value: 450000, purchase_value: 360000, _stub: true },
      { id: 2, name: 'Fixed Deposit',      asset_type: 'FD',         current_value: 200000, purchase_value: 200000, _stub: true },
      { id: 3, name: 'Equity Portfolio',   asset_type: 'STOCKS',     current_value: 380000, purchase_value: 300000, _stub: true },
    ]);
  }
});

module.exports = router;
