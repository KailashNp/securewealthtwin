// ─────────────────────────────────────────────────────────────────
// utils/auditLog.js – In-memory audit log
// Every action and its risk decision is stored here.
// In production, swap with a DB write (PostgreSQL / MongoDB).
// ─────────────────────────────────────────────────────────────────

const auditLog = [];

/**
 * Write an entry to the audit log.
 * @param {Object} entry - { actionId, userId, action_type, amount, decision, risk_score, timestamp, reason? }
 */
function writeAuditLog(entry) {
  auditLog.push(entry);
  console.log(`[AuditLog] ${entry.decision?.toUpperCase()} | user:${entry.userId} | ${entry.action_type} | ₹${entry.amount} | score:${entry.risk_score}`);
}

/**
 * Get audit log entries, optionally filtered by userId.
 * @param {number|null} userId
 */
function getAuditLog(userId = null) {
  if (userId) return auditLog.filter(e => e.userId === userId);
  return [...auditLog];
}

module.exports = { writeAuditLog, getAuditLog };
