import axios from "axios";

const API = import.meta.env.VITE_API_URL;

export const getProfile = (userId) =>
  axios.get(`${API}/api/user/${userId}/profile`);

export const executeAction = (payload) =>
  axios.post(`${API}/api/action/execute`, payload);

export const getExplanation = () =>
  axios.get(`${API}/api/recommend/explain`);