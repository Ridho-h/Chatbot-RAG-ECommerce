/**
 * Main application — orchestrates auth, chat, and admin views.
 */
import { useState } from 'react';
import useAuth from './hooks/useAuth';
import useChat from './hooks/useChat';
import LoginPage from './components/LoginPage';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ChatWindow from './components/ChatWindow';
import AdminPanel from './components/AdminPanel';

export default function App() {
  const auth = useAuth();
  const chat = useChat();
  const [currentView, setCurrentView] = useState('chat');

  // Show loading during initial auth check
  if (auth.loading && !auth.user) {
    return (
      <div className="login-page">
        <div className="login-bg" />
        <div style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>
          Loading...
        </div>
      </div>
    );
  }

  // Show login page if not authenticated
  if (!auth.isAuthenticated) {
    return (
      <LoginPage
        onLogin={auth.login}
        onRegister={auth.register}
        error={auth.error}
      />
    );
  }

  // Main app layout
  return (
    <div className="app-layout">
      <Sidebar
        sessions={chat.sessions}
        activeSessionId={chat.sessionId}
        onNewChat={chat.startNewChat}
        onSelectSession={chat.loadSession}
        onNavigate={setCurrentView}
        currentView={currentView}
        isAdmin={auth.isAdmin}
      />

      <div className="main-content">
        <Header
          user={auth.user}
          onLogout={auth.logout}
          currentView={currentView}
        />

        {currentView === 'chat' ? (
          <ChatWindow
            messages={chat.messages}
            isLoading={chat.isLoading}
            onSendMessage={chat.sendMessage}
          />
        ) : currentView === 'admin' && auth.isAdmin ? (
          <AdminPanel />
        ) : (
          <ChatWindow
            messages={chat.messages}
            isLoading={chat.isLoading}
            onSendMessage={chat.sendMessage}
          />
        )}
      </div>
    </div>
  );
}
