import HistoryItem from "./HistoryItem";
import Loader from "../common/Loader";
import ErrorMessage from "../common/ErrorMessage";
import "./HistoryList.css";

export default function HistoryList({ history, loading, error, onDelete, onRefresh }) {
  if (loading) {
    return <Loader text="Loading history..." />;
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!history || history.length === 0) {
    return (
      <div className="history-empty">
        <span className="empty-icon">📜</span>
        <h3>No history yet</h3>
        <p>Start analyzing text to build your creative history</p>
      </div>
    );
  }

  return (
    <div className="history-list">
      <div className="history-header">
        <h3>Your History</h3>
        {onRefresh && (
          <button className="refresh-btn" onClick={onRefresh}>
            ↻ Refresh
          </button>
        )}
      </div>
      <div className="history-items">
        {history.map((item) => (
          <HistoryItem key={item._id} item={item} onDelete={onDelete} />
        ))}
      </div>
    </div>
  );
}
