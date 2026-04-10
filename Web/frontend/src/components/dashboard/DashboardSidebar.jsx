import Loader from "../common/Loader";

export default function DashboardSidebar({
  sidebarOpen,
  handleNewChat,
  loadingChats,
  chatList,
  currentChatId,
  handleChatSelect,
  handleDeleteChat,
  user,
  logout,
}) {
  return (
    <aside className={`chat-sidebar ${sidebarOpen ? '' : 'closed'}`}>
      <div className="sidebar-header">
        <button className="new-chat-btn" onClick={handleNewChat}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          New chat
        </button>
      </div>

      <div className="sidebar-content">
        <div className="sidebar-section">
          <h3 className="sidebar-title">Recent Chats</h3>
          {loadingChats ? (
            <div className="sidebar-loading">
              <Loader size="sm" text="Loading chats..." />
            </div>
          ) : chatList.length > 0 ? (
            <div className="history-items">
              {chatList.map(chat => (
                <div
                  key={chat.id}
                  className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
                  onClick={() => handleChatSelect(chat.id)}
                >
                  <div className="history-text">{chat.title}</div>
                  <button
                    className="history-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(chat.id);
                    }}
                    title="Delete chat"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                    </svg>
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="sidebar-empty">No chats yet</div>
          )}
        </div>
      </div>

      <div className="sidebar-footer">
        <div className="user-menu">
          <div className="user-avatar-small">
            {user?.name?.charAt(0).toUpperCase() || "U"}
          </div>
          <span className="user-name-small">{user?.name}</span>
          <button className="logout-icon" onClick={logout} title="Logout">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>
  );
}
