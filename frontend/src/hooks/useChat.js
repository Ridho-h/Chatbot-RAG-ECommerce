import { useState, useCallback, useRef } from 'react';
import api from '../utils/api';

/**
 * Chat state management hook.
 * Handles messages, sessions, loading states, and API communication.
 */
export function useChat() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [sessions, setSessions] = useState([]);
  
  // Store messages by session ID
  const historyRef = useRef({});

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    // Add user message immediately
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => {
      const newMessages = [...prev, userMessage];
      if (sessionId) {
        historyRef.current[sessionId] = newMessages;
      } else {
        historyRef.current['temp'] = newMessages;
      }
      return newMessages;
    });
    setIsLoading(true);

    try {
      const data = await api.sendMessage(text, sessionId);

      let currentSessionId = sessionId;

      // Update session ID if it's new
      if (data.session_id && data.session_id !== sessionId) {
        setSessionId(data.session_id);
        currentSessionId = data.session_id;
        // Transfer temp history to new session id
        if (historyRef.current['temp']) {
          historyRef.current[data.session_id] = historyRef.current['temp'];
          delete historyRef.current['temp'];
        }
      }

      // Add bot response
      const botMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: data.response,
        sources: data.sources || [],
        thinkingTime: data.thinking_time_ms,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => {
        const newMessages = [...prev, botMessage];
        historyRef.current[currentSessionId] = newMessages;
        return newMessages;
      });

      // Update sessions list
      setSessions((prev) => {
        const existing = prev.find((s) => s.id === data.session_id);
        if (existing) {
          return prev.map((s) =>
            s.id === data.session_id
              ? { ...s, lastMessage: text, updatedAt: new Date().toISOString() }
              : s
          );
        }
        return [
          {
            id: data.session_id,
            firstMessage: text,
            lastMessage: text,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
          ...prev,
        ];
      });
    } catch (err) {
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: `Sorry, an error occurred: ${err.message}`,
        isError: true,
        timestamp: new Date().toISOString(),
      };
      setMessages((prev) => {
        const newMessages = [...prev, errorMessage];
        if (sessionId) historyRef.current[sessionId] = newMessages;
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, sessionId]);

  const startNewChat = useCallback(() => {
    // If we have an active session, ensure its history is saved
    if (sessionId) {
      historyRef.current[sessionId] = messages;
    }
    setMessages([]);
    setSessionId(null);
  }, [sessionId, messages]);

  const loadSession = useCallback((sid) => {
    // Save current session before switching
    if (sessionId) {
      historyRef.current[sessionId] = messages;
    }
    setSessionId(sid);
    setMessages(historyRef.current[sid] || []);
  }, [sessionId, messages]);

  return {
    messages,
    sessionId,
    isLoading,
    sessions,
    sendMessage,
    startNewChat,
    loadSession,
  };
}

export default useChat;
