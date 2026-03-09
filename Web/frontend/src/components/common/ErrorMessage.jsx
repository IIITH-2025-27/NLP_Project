import "./ErrorMessage.css";

export default function ErrorMessage({ message, onClose }) {
  if (!message) return null;

  return (
    <div className="error-message">
      <span className="error-icon">⚠️</span>
      <span className="error-text">{message}</span>
      {onClose && (
        <button className="error-close" onClick={onClose} aria-label="Close">
          ✕
        </button>
      )}
    </div>
  );
}
