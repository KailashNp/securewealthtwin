// src/hooks/useSecurityGate.js
import axios from 'axios';

export const useSecurityGate = (setModalState) => {
  const API = process.env.REACT_APP_API_URL;

  const executeWithSecurity = async (actionType, payload, actualFunction) => {
    try {
      // 1. CALL FRAUD CHECK FIRST (Port 8000)
      const res = await axios.post(`${API}/api/action/execute`, { 
        actionType, 
        ...payload 
      });

      // 2. OPEN MODAL (Logic inside Modal handles the 'actualFunction' call on confirm)
      setModalState({
        isOpen: true,
        decision: res.data.decision,
        riskScore: res.data.riskScore,
        message: res.data.message,
        onConfirm: actualFunction // Pass the intent to be called later
      });
    } catch (err) {
      console.error("Security Offline", err);
      // Fallback: BLOCK for safety
      setModalState({ isOpen: true, decision: 'BLOCK', message: "Security Gateway Unreachable." });
    }
  };

  return { executeWithSecurity };
};