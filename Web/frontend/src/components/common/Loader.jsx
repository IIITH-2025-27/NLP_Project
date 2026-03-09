import "./Loader.css";

export default function Loader({ size = "md", text = "" }) {
  return (
    <div className={`loader-container loader-${size}`}>
      <div className="loader-spinner">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <span className="spinner-icon">𝄞</span>
      </div>
      {text && <p className="loader-text">{text}</p>}
    </div>
  );
}
