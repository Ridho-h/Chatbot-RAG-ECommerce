import { useState } from 'react';

/**
 * Login / Register page with glassmorphism design.
 */
export default function LoginPage({ onLogin, onRegister, error }) {
  const [activeTab, setActiveTab] = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [localError, setLocalError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLocalError(null);
    setLoading(true);

    try {
      if (activeTab === 'login') {
        await onLogin(username, password);
      } else {
        await onRegister(username, password);
      }
    } catch (err) {
      setLocalError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const displayError = localError || error;

  return (
    <div className="login-page">
      <div className="login-bg" />
      <div className="login-card">
        <div className="login-logo">
          <div className="logo-icon">🛒</div>
          <h2>ShopAI</h2>
          <p className="login-subtitle">Smart E-Commerce Assistant</p>
        </div>

        <div className="login-tabs">
          <button
            className={`login-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => { setActiveTab('login'); setLocalError(null); }}
          >
            Sign In
          </button>
          <button
            className={`login-tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => { setActiveTab('register'); setLocalError(null); }}
          >
            Sign Up
          </button>
        </div>

        {displayError && (
          <div className="login-error">{displayError}</div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              minLength={3}
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
              minLength={4}
              autoComplete={activeTab === 'login' ? 'current-password' : 'new-password'}
            />
          </div>

          <button
            type="submit"
            className="login-btn"
            disabled={loading || !username || !password}
          >
            {loading
              ? 'Please wait...'
              : activeTab === 'login'
                ? 'Sign In'
                : 'Create Account'
            }
          </button>
        </form>

        {activeTab === 'login' && (
          <p style={{ textAlign: 'center', marginTop: '16px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            Demo admin: admin / admin123
          </p>
        )}
      </div>
    </div>
  );
}
