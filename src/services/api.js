import axios from "axios";

const API = process.env.REACT_APP_API_URL;

export const getProfile = (userId) =>
  axios.get(`${API}/api/user/${userId}/profile`);

export const executeAction = (payload) =>
  axios.post(`${API}/api/action/execute`, payload);

export const getExplanation = (payload) =>
  axios.get(`${API}/api/recommend/explain`, payload );