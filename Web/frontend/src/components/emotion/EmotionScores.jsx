import { getEmotionColor } from "../../utils/helpers";
import "./EmotionScores.css";

export default function EmotionScores({ scores }) {
  if (!scores) return null;

  const sortedScores = Object.entries(scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  return (
    <div className="emotion-scores">
      <h4 className="scores-title">Emotion Breakdown</h4>
      <div className="scores-list">
        {sortedScores.map(([emotion, score]) => (
          <div key={emotion} className="score-item">
            <div className="score-header">
              <span className="score-emotion">{emotion}</span>
              <span className="score-value">{Math.round(score * 100)}%</span>
            </div>
            <div className="score-bar">
              <div 
                className="score-fill" 
                style={{ 
                  width: `${Math.round(score * 100)}%`,
                  backgroundColor: getEmotionColor(emotion)
                }} 
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
