import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

const http = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

export async function createAudit(payload) {
  const { data } = await http.post("/audit/", payload);
  return data;
}

export async function getStatus(jobId) {
  const { data } = await http.get(`/audit/${jobId}/status`);
  return data;
}

export async function getFindings(jobId) {
  const { data } = await http.get(`/audit/${jobId}/findings`);
  return data;
}

export async function getReport(jobId) {
  const { data } = await http.get(`/audit/${jobId}/report`);
  return data;
}

export function getPdfUrl(jobId) {
  return `${BASE_URL}/audit/${jobId}/report/pdf`;
}

export async function pollLog(jobId, since = 0) {
  const { data } = await http.get(`/audit/${jobId}/log?since=${since}`);
  return data;
}

export function openStream(jobId) {
  return new WebSocket(`${WS_URL}/ws/audit/${jobId}/stream`);
}