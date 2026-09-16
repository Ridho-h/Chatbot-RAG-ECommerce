/**
 * Sidebar with logo, new chat button, chat sessions list, and admin navigation.
 */
export default function Sidebar({
  sessions,
  activeSessionId,
  onNewChat,
  onSelectSession,
  onNavigate,
  currentView,
  isAdmin,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">🛒</div>
          <div>
            <h1>ShopAI</h1>
            <p>E-Commerce Assistant</p>
          </div>
        </div>

        <button className="new-chat-btn" onClick={onNewChat}>
          ＋ New Chat
        </button>
      </div>

      <div className="sidebar-sessions">
        {sessions.length === 0 ? (
          <p style={{ padding: '12px', fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center' }}>
            No conversations yet
          </p>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => onSelectSession(session.id)}
              title={session.firstMessage}
            >
              💬 {session.firstMessage || 'New conversation'}
            </div>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button
          className={`sidebar-nav-btn ${currentView === 'chat' ? 'active' : ''}`}
          onClick={() => onNavigate('chat')}
        >
          💬 Chat
        </button>
        {isAdmin && (
          <button
            className={`sidebar-nav-btn admin-btn ${currentView === 'admin' ? 'active' : ''}`}
            onClick={() => onNavigate('admin')}
          >
            ⚙️ Admin Panel
          </button>
        )}
      </div>
    </aside>
  );
}
