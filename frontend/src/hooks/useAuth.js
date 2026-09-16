import { useState, useCallback, useEffect } from 'react';
import api from '../utils/api';

/**
 * Auth state management hook.
 * Handles login, register, logout, and persisted auth state.
 */
export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check for existing session on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    if (token && savedUser) {
      try {
        setUser(JSON.parse(savedUser));
        api.setToken(token);
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = useCallback(async (username, password) => {
    setError(null);
    setLoading(true);
    try {
      const data = await api.login(username, password);
      const userData = {
        username: data.username,
        role: data.role,
      };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (username, password) => {
    setError(null);
    setLoading(true);
    try {
      const data = await api.register(username, password);
      const userData = {
        username: data.username,
        role: data.role,
      };
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return userData;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    api.setToken(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }, []);

  const isAdmin = user?.role === 'admin';

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    isAdmin,
    isAuthenticated: !!user,
  };
}

export default useAuth;
