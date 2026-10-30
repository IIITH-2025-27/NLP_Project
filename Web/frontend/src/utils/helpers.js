/**
 * Format date to readable string
 */
export const formatDate = (dateString) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now - date;
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);

  if (seconds < 60) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
};

/**
 * Truncate text to specified length
 */
export const truncateText = (text, maxLength = 60) => {
  if (!text || text.length <= maxLength) return text;
  return text.slice(0, maxLength) + "…";
};

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    console.error("Failed to copy:", err);
    return false;
  }
};

/**
 * Validate email format
 */
export const isValidEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

/**
 * Get emotion color (6 FER emotions)
 */
export const getEmotionColor = (emotion) => {
  const colors = {
    Happy: "#FFD93D",
    Sad: "#6BA3BE",
    Angry: "#FF6B6B",
    Fear: "#845EC2",
    Surprise: "#4ECDC4",
    Neutral: "#95A5A6",
  };
  return colors[emotion] || "#888";
};

/**
 * Format confidence percentage
 */
export const formatConfidence = (confidence) => {
  return Math.round(confidence * 100);
};

/**
 * Debounce function
 */
export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Downscale an image in the browser before upload so uploads stay fast and the
 * previews stored in MongoDB stay small. Longest side <= maxSize, re-encoded as JPEG.
 * Returns { file, dataUrl }.
 */
export const resizeImageFile = (file, maxSize = 1280, quality = 0.85) =>
  new Promise((resolve, reject) => {
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => {
      URL.revokeObjectURL(url);
      const scale = Math.min(1, maxSize / Math.max(img.width, img.height));
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#fff"; // JPEG has no alpha; avoid black backgrounds on transparent PNGs
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      const dataUrl = canvas.toDataURL("image/jpeg", quality);
      canvas.toBlob(
        (blob) => {
          if (!blob) return reject(new Error("Could not process this image"));
          const name = (file.name || "image").replace(/\.[^.]+$/, "") + ".jpg";
          resolve({ file: new File([blob], name, { type: "image/jpeg" }), dataUrl });
        },
        "image/jpeg",
        quality
      );
    };
    img.onerror = () => {
      URL.revokeObjectURL(url);
      reject(new Error("Could not read this image. Please try a JPG or PNG."));
    };
    img.src = url;
  });
