/**
 * Admin panel — metrics dashboard, RAGAS scores, and admin actions.
 * Only accessible to users with the "admin" role.
 */
import { useState, useEffect, useCallback } from 'react';
import api from '../utils/api';

export default function AdminPanel() {
  const [metrics, setMetrics] = useState(null);
  const [evalResults, setEvalResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionStatus, setActionStatus] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [metricsData, evalData] = await Promise.all([
        api.getMetrics(),
        api.getEvalResults().catch(() => null),
      ]);
      setMetrics(metricsData);
      setEvalResults(evalData);
    } catch (err) {
      console.error('Failed to fetch admin data:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleIngest = async () => {
    setActionStatus('Ingesting data... This may take several minutes.');
    try {
      const result = await api.triggerIngestion();
      setActionStatus(`✅ ${result.message} (${result.total_vectors} vectors)`);
      fetchData();
    } catch (err) {
      setActionStatus(`❌ Ingestion failed: ${err.message}`);
    }
  };

  const handleCleanup = async () => {
    try {
      const result = await api.cleanupSessions();
      setActionStatus(`✅ Cleaned up ${result.sessions_removed} expired sessions`);
      fetchData();
    } catch (err) {
      setActionStatus(`❌ Cleanup failed: ${err.message}`);
    }
  };

  const getScoreClass = (score) => {
    if (score >= 0.7) return 'good';
    if (score >= 0.4) return 'ok';
    return 'bad';
  };

  if (loading) {
    return (
      <div className="admin-panel">
        <h2>Admin Dashboard</h2>
        <p style={{ color: 'var(--text-secondary)' }}>Loading metrics...</p>
      </div>
    );
  }

  return (
    <div className="admin-panel">
      <h2>📊 Admin Dashboard</h2>

      {/* ── Metrics Grid ────────────────────────────────────── */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Active Sessions</div>
          <div className="metric-value">{metrics?.active_sessions ?? '—'}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">LLM Provider</div>
          <div className="metric-value" style={{ fontSize: '1.1rem' }}>
            {metrics?.llm_provider ?? '—'}
          </div>
          <div className="metric-sub">{metrics?.llm_model}</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Search Provider</div>
          <div className="metric-value" style={{ fontSize: '1.1rem' }}>
            {metrics?.search_provider ?? '—'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Rate Limit</div>
          <div className="metric-value">{metrics?.rate_limit_per_minute ?? '—'}</div>
          <div className="metric-sub">requests/min</div>
        </div>
        <div className="metric-card">
          <div className="metric-label">LangSmith Tracing</div>
          <div className="metric-value" style={{ fontSize: '1.1rem' }}>
            {metrics?.langsmith_enabled ? '✅ Enabled' : '⚫ Disabled'}
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-label">Embedding Model</div>
          <div className="metric-value" style={{ fontSize: '0.85rem' }}>
            {metrics?.embedding_model?.split('/').pop() ?? '—'}
          </div>
        </div>
      </div>

      {/* ── Custom Evaluation ────────────────────────────────── */}
      <div className="admin-section">
        <h3>📈 Evaluation Metrics</h3>
        {evalResults?.results ? (
          <>
            <div className="metrics-grid" style={{ marginBottom: '20px' }}>
              <div className="metric-card">
                <div className="metric-label">Success Rate</div>
                <div className={`metric-value ${parseFloat(evalResults.results.success_rate) >= 80 ? 'good' : 'bad'}`}>
                  {evalResults.results.success_rate}
                </div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Questions Evaluated</div>
                <div className="metric-value">{evalResults.results.total_questions}</div>
              </div>
              <div className="metric-card">
                <div className="metric-label">Evaluation Time</div>
                <div className="metric-value">{evalResults.results.evaluation_time_seconds}s</div>
              </div>
            </div>
            
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                    <th style={{ padding: '8px' }}>Question</th>
                    <th style={{ padding: '8px' }}>Docs Retrieved</th>
                    <th style={{ padding: '8px' }}>Status</th>
                    <th style={{ padding: '8px' }}>Answer Preview</th>
                  </tr>
                </thead>
                <tbody>
                  {evalResults.results.details?.map((detail, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '8px' }}>{detail.question}</td>
                      <td style={{ padding: '8px', textAlign: 'center' }}>{detail.retrieved_docs_count}</td>
                      <td style={{ padding: '8px', color: detail.answered ? 'var(--accent-color)' : 'red' }}>
                        {detail.answered ? 'Answered' : 'Failed'}
                      </td>
                      <td style={{ padding: '8px', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {detail.answer_preview}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p style={{ marginTop: '16px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Last evaluated: {evalResults.results.timestamp}
            </p>
          </>
        ) : (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            No evaluation results yet. Run: <code>docker exec chatbot-backend python scripts/evaluate.py</code>
          </p>
        )}
      </div>

      {/* ── Admin Actions ───────────────────────────────────── */}
      <div className="admin-section">
        <h3>🔧 Actions</h3>
        <button className="admin-action-btn" onClick={handleIngest}>
          🔄 Re-ingest Dataset
        </button>
        <button className="admin-action-btn" onClick={handleCleanup}>
          🧹 Cleanup Expired Sessions
        </button>
        <button className="admin-action-btn" onClick={fetchData}>
          🔃 Refresh Metrics
        </button>
      </div>

      {actionStatus && (
        <div style={{
          padding: '12px 16px',
          background: 'var(--bg-tertiary)',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.85rem',
          color: 'var(--text-secondary)',
          marginTop: '16px',
        }}>
          {actionStatus}
        </div>
      )}
    </div>
  );
}
