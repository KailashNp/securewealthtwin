// ─────────────────────────────────────────────────────────────────
// middleware/auth.js – JWT verification middleware
// Attach to any route that requires a logged-in user.
// ─────────────────────────────────────────────────────────────────

const jwt = require('jsonwebtoken');
const JWT_SECRET = process.env.JWT_SECRET || 'changeme';

/**
 * Verifies the Bearer token in the Authorization header.
 * On success, attaches `req.user` (the decoded JWT payload).
 */
function verifyToken(req, res, next) {
  const authHeader = req.headers['authorization'];
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header' });
  }

  const token = authHeader.split(' ')[1];
  try {
    req.user = jwt.verify(token, JWT_SECRET);
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }
}

module.exports = { verifyToken };
