/**
 * CloudRescue API Client
 * Fetches verified experimental data from the read-only FastAPI backend.
 */

const API_BASE = '/api';

export async function fetchSummary() {
  const res = await fetch(`${API_BASE}/summary`);
  if (!res.ok) throw new Error('Failed to fetch summary');
  return res.json();
}

export async function fetchScenarios() {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch scenarios');
  return res.json();
}

export async function fetchBenchmarks(scenario = null) {
  const url = scenario ? `${API_BASE}/benchmarks?scenario=${scenario}` : `${API_BASE}/benchmarks`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch benchmarks');
  return res.json();
}

export async function fetchAnalytics(scenario = null) {
  const url = scenario ? `${API_BASE}/analytics?scenario=${scenario}` : `${API_BASE}/analytics`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch analytics');
  return res.json();
}

export async function fetchTimeseries(scenario, config, seed, step = 2) {
  const res = await fetch(`${API_BASE}/timeseries/${scenario}/${config}/${seed}?step=${step}`);
  if (!res.ok) throw new Error('Failed to fetch timeseries');
  return res.json();
}

export async function fetchRecoveryMetrics() {
  const res = await fetch(`${API_BASE}/recovery`);
  if (!res.ok) throw new Error('Failed to fetch recovery metrics');
  return res.json();
}

export async function fetchSensitivity() {
  const res = await fetch(`${API_BASE}/sensitivity`);
  if (!res.ok) throw new Error('Failed to fetch sensitivity');
  return res.json();
}

export async function fetchStatistics() {
  const res = await fetch(`${API_BASE}/statistics`);
  if (!res.ok) throw new Error('Failed to fetch statistics');
  return res.json();
}

export async function fetchPublication() {
  const res = await fetch(`${API_BASE}/publication`);
  if (!res.ok) throw new Error('Failed to fetch publication content');
  return res.json();
}
