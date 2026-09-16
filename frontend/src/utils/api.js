/**
 * API client — centralized HTTP calls with auth header injection.
 */

const API_BASE = '/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getToken() {
    return this.token || localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    // Handle 401 — token expired (only for authenticated requests, not login/register)
    const isAuthEndpoint = endpoint === '/auth/login' || endpoint === '/auth/register';
    if (response.status === 401 && !isAuthEndpoint) {
      this.setToken(null);
      window.location.reload();
      throw new Error('Session expired. Please login again.');
    }

    if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please wait a moment.');
    }

    let data;
    try {
      data = await response.json();
    } catch {
      data = { detail: `Request failed with status ${response.status}` };
    }

    if (!response.ok) {
      throw new Error(data.detail || `Request failed: ${response.status}`);
    }

    return data;
  }

  // ── Auth ────────────────────────────────────────────────────────
  async login(username, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(username, password) {
    const data = await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  // ── Chat ────────────────────────────────────────────────────────
  async sendMessage(message, sessionId = null) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  }

  // ── Admin ───────────────────────────────────────────────────────
  async getMetrics() {
    return this.request('/admin/metrics');
  }

  async triggerIngestion() {
    return this.request('/admin/ingest', { method: 'POST' });
  }

  async getEvalResults() {
    return this.request('/admin/eval');
  }

  async cleanupSessions() {
    return this.request('/admin/cleanup-sessions', { method: 'POST' });
  }

  // ── Health ──────────────────────────────────────────────────────
  async healthCheck() {
    const response = await fetch('/health');
    return response.json();
  }
}

export const api = new ApiClient();
export default api;
