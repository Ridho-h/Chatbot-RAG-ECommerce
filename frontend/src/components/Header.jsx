/**
 * App header with user info and logout button.
 */
export default function Header({ user, onLogout, currentView }) {
  const viewTitles = {
    chat: '💬 Chat',
    admin: '⚙️ Admin Dashboard',
  };

  return (
    <header className="header">
      <div className="header-left">
        <h2 className="header-title">{viewTitles[currentView] || 'Chat'}</h2>
      </div>

      <div className="header-right">
        <div className="header-user">
          <div className="user-avatar">
            {user?.username?.charAt(0).toUpperCase() || 'U'}
          </div>
          <div className="user-info">
            <span className="user-name">{user?.username}</span>
            <span className="user-role">{user?.role}</span>
          </div>
        </div>

        <button className="logout-btn" onClick={onLogout}>
          Logout
        </button>
      </div>
    </header>
  );
}
