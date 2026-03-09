import { getEmotionColor, formatConfidence } from "../../utils/helpers";
import { EMOTION_EMOJIS, EMOTION_DESCRIPTIONS } from "../../utils/constants";
import "./EmotionBadge.css";

export default function EmotionBadge({ emotion, confidence, meta }) {
  const color = getEmotionColor(emotion);
  const emoji = meta?.emoji || EMOTION_EMOJIS[emotion] || "❓";
  const description = meta?.description || EMOTION_DESCRIPTIONS[emotion] || "";

  return (
    <div className="emotion-badge" style={{ "--emotion-color": color }}>
      <span className="emotion-emoji">{emoji}</span>
      <div className="emotion-info">
        <span className="emotion-name">{emotion}</span>
        <span className="emotion-desc">{description}</span>
      </div>
      <div className="emotion-confidence">
        <div className="confidence-bar">
          <div 
            className="confidence-fill" 
            style={{ width: `${formatConfidence(confidence)}%` }} 
          />
        </div>
        <span className="confidence-label">{formatConfidence(confidence)}%</span>
      </div>
    </div>
  );
}
