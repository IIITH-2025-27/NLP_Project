import Loader from "../common/Loader";
import LyricsCard from "../lyrics/LyricsCard";

export default function DashboardLyricsPanel({
  selectedRequestIndex,
  handleRequestDropdownChange,
  loadingMessages,
  isAnalyzing,
  progressText,
  slow,
  requests,
  selectedRequest,
  isScoring,
}) {
  const isErrorRequest = Boolean(selectedRequest?.emotion?.meta?.is_error);
  const emotionName = selectedRequest?.emotion?.emotion || "Unknown";
  const emotionDescription = selectedRequest?.emotion?.meta?.description || "";
  const emotionEmoji = selectedRequest?.emotion?.meta?.emoji || "❓";
  const confidence = selectedRequest?.emotion?.confidence;
  // The image model returns only a label, so its "confidence" is not a real probability.
  const showConfidence =
    typeof confidence === "number" && !isErrorRequest && selectedRequest?.input_type !== "image";
  const loaderText = slow
    ? `${progressText || "Working..."} This can take up to a minute if the servers are waking up.`
    : progressText || "Saving...";

  return (
    <aside className={`lyrics-panel ${isAnalyzing ? "is-analyzing" : ""}`}>
      <div className="lyrics-panel-header">
        <label htmlFor="request-select" className="request-label">Select Request:</label>
        <select
          id="request-select"
          className="request-dropdown"
          value={selectedRequestIndex !== null ? selectedRequestIndex : ''}
          onChange={(e) => handleRequestDropdownChange(e.target.value)}
          disabled={loadingMessages || isAnalyzing || requests.length === 0}
        >
          <option value="">Select a request...</option>
          {requests.map((_, index) => (
            <option key={index} value={index}>
              Request {index + 1}
            </option>
          ))}
        </select>
      </div>

      <div className="lyrics-panel-content">
        {loadingMessages ? (
          <div className="lyrics-empty">
            <Loader size="md" text="Loading requests..." />
          </div>
        ) : selectedRequest ? (
          <div className={`lyrics-display ${isAnalyzing ? "is-loading" : ""}`}>
            <div className="lyrics-emotion-compact">
              <span className="lyrics-emoji">{emotionEmoji}</span>
              <div className="lyrics-emotion-info">
                <span className="lyrics-emotion-name">{emotionName}</span>
                <span className="lyrics-emotion-desc">{emotionDescription}</span>
              </div>
              {showConfidence && (
                <div className="lyrics-confidence-badge">
                  {Math.round(confidence * 100)}%
                </div>
              )}
            </div>
            <div className="lyrics-text-section">
              <LyricsCard
                lyrics={selectedRequest.lyrics || "Invalid input"}
                emotion={emotionName}
                score={selectedRequest.lyrics_score}
                scoring={isScoring}
              />
            </div>
            {isAnalyzing && (
              <div className="lyrics-loading-overlay" aria-live="polite">
                <Loader size="md" text={loaderText} />
              </div>
            )}
          </div>
        ) : isAnalyzing ? (
          <div className="lyrics-empty">
            <Loader size="md" text={loaderText} />
          </div>
        ) : (
          <div className="lyrics-empty">
            <div className="lyrics-empty-icon">🎵</div>
            <p>Select a request to view lyrics</p>
          </div>
        )}
      </div>
    </aside>
  );
}
