// ─────────────────────────────────────────────────────────────────
// routes/chat.js – Proxy to Chat Service
// POST /api/chat/message
// ─────────────────────────────────────────────────────────────────

const express = require('express');
const axios = require('axios');
const { verifyToken } = require('../middleware/auth');
const router = express.Router();

const CHAT_URL = process.env.CHAT_SERVICE_URL || 'http://localhost:8003';

/**
 * POST /api/chat/message
 * Body: { userId, message, history? }
 *
 * Response format (chat service must return exactly this):
 * { reply: string, reasoning: string }
 */
router.post('/message', verifyToken, async (req, res) => {
  const { userId, message, history } = req.body;

  if (!userId || !message) {
    return res.status(400).json({ error: 'userId and message are required' });
  }

  try {
    const response = await axios.post(`${CHAT_URL}/chat`, {
      user_id: userId,
      message,
      history: history || [],
    }, { timeout: 15000 });

    // Enforce response shape
    const { reply, reasoning } = response.data;
    return res.json({ reply: reply || response.data.reply, reasoning: reasoning || '' });
  } catch (err) {
    console.warn('[Chat] Chat Service unreachable — returning stub reply');
    return res.json({
      reply: "I'm your SecureWealth AI advisor. I can help you with investments, savings, and financial planning. The AI service is currently initializing — please try again in a moment.",
      reasoning: 'Chat service stub response',
      _stub: true,
    });
  }
});

module.exports = router;
