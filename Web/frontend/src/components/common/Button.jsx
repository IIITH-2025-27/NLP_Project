import "./Button.css";

export default function Button({ 
  children, 
  onClick, 
  variant = "primary", 
  disabled = false, 
  type = "button",
  fullWidth = false,
  loading = false,
  ...props 
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} ${fullWidth ? 'btn-full' : ''} ${loading ? 'btn-loading' : ''}`}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? <span className="btn-spinner" /> : children}
    </button>
  );
}
