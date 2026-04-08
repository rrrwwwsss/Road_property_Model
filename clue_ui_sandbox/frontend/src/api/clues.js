import axios from "axios";

const http = axios.create({ timeout: 15000 });

export async function fetchClues(params) {
  const { data } = await http.get("/api/clues", { params });
  return data;
}

export async function fetchClueDetail(id) {
  const { data } = await http.get(`/api/clues/${id}`);
  return data;
}

export async function commitClue(id) {
  const { data } = await http.post(`/api/clues/${id}/commit`);
  return data;
}

export async function fetchStatsSummary() {
  const { data } = await http.get("/api/stats/summary");
  return data;
}

export async function fetchStatsByUnit() {
  const { data } = await http.get("/api/stats/by-violation");
  return data;
}

export async function fetchStatsByMeasure() {
  const { data } = await http.get("/api/stats/by-location");
  return data;
}

export async function fetchTrendByViolation() {
  const { data } = await http.get("/api/stats/trend-by-violation");
  return data;
}
