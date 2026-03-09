import { useState } from "react";
import { copyToClipboard } from "../../utils/helpers";
import { getEmotionColor } from "../../utils/helpers";
import Button from "../common/Button";
import "./LyricsCard.css";

export default function LyricsCard({ lyrics, emotion }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const success = await copyToClipboard(lyrics);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const color = getEmotionColor(emotion);

  return (
    <div className="lyrics-card" style={{ "--emotion-color": color }}>
      <div className="lyrics-header">
        <span className="lyrics-label">✦ Generated Lyrics</span>
        <Button 
          variant="secondary" 
          onClick={handleCopy}
          disabled={copied}
        >
          {copied ? "✓ Copied!" : "Copy"}
        </Button>
      </div>
      <pre className="lyrics-text">{lyrics}</pre>
    </div>
  );
}
