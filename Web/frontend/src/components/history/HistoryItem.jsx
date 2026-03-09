import { useState } from "react";
import { truncateText, formatDate, getEmotionColor } from "../../utils/helpers";
import Button from "../common/Button";
import "./HistoryItem.css";

export default function HistoryItem({ item, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(item._id);
    setDeleting(false);
  };

  const color = getEmotionColor(item.emotion);

  return (
    <div className="history-item" style={{ "--emotion-color": color }}>
      <div className="history-top" onClick={() => setExpanded(!expanded)}>
        <div className="history-left">
          <span className="history-dot" />
          <span className="history-text">{truncateText(item.input_text, 60)}</span>
        </div>
        <div className="history-right">
          <span className="history-emotion">{item.emotion}</span>
          <span className="history-chevron">{expanded ? "▲" : "▼"}</span>
        </div>
      </div>
      
      {expanded && (
        <div className="history-expanded">
          <div className="history-section">
            <h5>Your Input</h5>
            <p className="history-full-text">"{item.input_text}"</p>
          </div>
          
          <div className="history-section">
            <h5>Generated Lyrics</h5>
            <pre className="history-lyrics">{item.lyrics}</pre>
          </div>
          
          <div className="history-actions">
            <span className="history-date">{formatDate(item.created_at)}</span>
            <Button 
              variant="danger" 
              onClick={handleDelete}
              loading={deleting}
            >
              Delete
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
