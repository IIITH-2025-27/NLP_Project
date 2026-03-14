import { useState } from "react";
import Loader from "../common/Loader";

export default function DashboardChatSection({
  loadingChats,
  loadingMessages,
  currentMessages,
  examplePrompts,
  setText,
  requestRefs,
  user,
  getUserRequestNumber,
  handleMessageSelect,
  setPreprocessedImageToShow,
  setPreprocessedModalOpen,
  handleRetryRequest,
  loading,
  retryingAssistantId,
  regeneratedAssistantIds,
  pendingUserMessage,
  pendingRequestNum,
  retryContext,
  inputMode,
  messagesEndRef,
  sidebarOpen,
  setSidebarOpen,
  handleModeSwitch,
  textareaRef,
  text,
  maxTextLength,
  handleKeyDown,
  handleAnalyze,
  imagePreview,
  fileInputRef,
  handleImageSelect,
  handleCameraOpen,
  handleRemoveImage,
  handleEditTextRequest,
  openImageEditModal,
}) {
  const [editingTextMessageId, setEditingTextMessageId] = useState(null);
  const [editingTextValue, setEditingTextValue] = useState("");

  const startTextEdit = (message) => {
    setEditingTextMessageId(message.id);
    setEditingTextValue(message.content || "");
  };

  const cancelTextEdit = () => {
    setEditingTextMessageId(null);
    setEditingTextValue("");
  };

  const submitTextEdit = async (message) => {
    const nextText = editingTextValue.trim();
    if (!nextText) return;
    await handleEditTextRequest(message, nextText);
    cancelTextEdit();
  };

  const renderGeneratedStatus = (msg) => {
    if (!msg?.lyrics && retryingAssistantId !== msg?.id) return null;

    return (
      <p className="message-text assistant-status-text user-generated-status">
        {retryingAssistantId === msg.id ? (
          <span className="assistant-status-inline">
            <svg className="assistant-status-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12a9 9 0 00-9-9"/>
              <path d="M3 12a9 9 0 009 9" opacity="0.35"/>
            </svg>
            Regenerating lyrics...
          </span>
        ) : msg.emotion?.meta?.is_error ? (
          msg.emotion?.meta?.description || msg.content || "Invalid input"
        ) : regeneratedAssistantIds[msg.id] ? (
          "Lyrics regenerated successfully ✓"
        ) : (
          "Lyrics generated successfully ✓"
        )}
      </p>
    );
  };

  return (
    <main className="chat-main">
      <header className="chat-header">
        <button
          className="sidebar-toggle"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M3 12h18M3 6h18M3 18h18"/>
          </svg>
        </button>
        <h1 className="chat-title">LyricMind</h1>
      </header>

      <div className="chat-messages">
        {loadingChats || loadingMessages ? (
          <div className="welcome-screen">
            <Loader size="lg" text={loadingChats ? "Loading dashboard..." : "Loading messages..."} />
          </div>
        ) : currentMessages.length === 0 && !pendingUserMessage && !loading ? (
          <div className="welcome-screen">
            <div className="welcome-icon">𝄞</div>
            <h2 className="welcome-title">LyricMind</h2>
            <p className="welcome-subtitle">Express yourself and transform your emotions into lyrical art</p>

            <div className="example-prompts">
              {examplePrompts.map((prompt, idx) => (
                <button
                  key={idx}
                  className="example-prompt"
                  onClick={() => setText(prompt.text)}
                >
                  <span className="prompt-emoji">{prompt.emoji}</span>
                  <span className="prompt-text">{prompt.text}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {currentMessages.map((msg, index) => {
              const requestNum = msg.message_type === 'user' ? getUserRequestNumber(index) : null;

              return (
                <div
                  key={msg.id}
                  className={`message ${msg.message_type}`}
                  ref={(el) => {
                    requestRefs.current[msg.id] = el;
                  }}
                  onClick={() => handleMessageSelect(msg, index)}
                  style={{ cursor: "pointer" }}
                >
                  <div className="message-avatar">
                    {msg.message_type === 'user' ? (
                      <span>{requestNum || user?.name?.charAt(0).toUpperCase() || "U"}</span>
                    ) : (
                      <span>𝄞</span>
                    )}
                  </div>
                  <div className="message-content">
                    {msg.message_type === 'user' && msg.input_type === 'image' && msg.image_preview ? (
                      <>
                        <div className="message-image">
                          <img src={msg.image_preview} alt="Uploaded" />
                          {msg.preprocessed_image && (
                            <button
                              className="preprocessed-view-btn"
                              onClick={(e) => {
                                e.stopPropagation();
                                setPreprocessedImageToShow(msg.preprocessed_image);
                                setPreprocessedModalOpen(true);
                              }}
                              title="View preprocessed image (224×224 face)"
                            >
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                                <circle cx="12" cy="12" r="3"/>
                              </svg>
                            </button>
                          )}
                          <button
                            className="image-edit-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              openImageEditModal(msg);
                            }}
                            title="Edit image input"
                            disabled={loading}
                          >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M12 20h9"/>
                              <path d="M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4 12.5-12.5z"/>
                            </svg>
                          </button>
                          <button
                            className="image-retry-btn"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRetryRequest(msg);
                            }}
                            title="Retry this request"
                            disabled={loading}
                          >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                              <path d="M23 4v6h-6"/>
                              <path d="M1 20v-6h6"/>
                              <path d="M3.51 9a9 9 0 0114.13-3.36L23 10"/>
                              <path d="M20.49 15a9 9 0 01-14.13 3.36L1 14"/>
                            </svg>
                          </button>
                        </div>
                        {renderGeneratedStatus(msg)}
                      </>
                    ) : (
                      <>
                        {msg.message_type === 'user' ? (
                          <>
                            <div className={`user-text-bubble ${editingTextMessageId === msg.id ? "editing" : ""}`}>
                              {editingTextMessageId === msg.id ? (
                                <div className="inline-text-edit" onClick={(e) => e.stopPropagation()}>
                                  <textarea
                                    className="inline-edit-input"
                                    value={editingTextValue}
                                    onChange={(e) => setEditingTextValue(e.target.value)}
                                    maxLength={maxTextLength}
                                    rows={4}
                                    disabled={loading}
                                    onKeyDown={(e) => {
                                      if (e.key === "Enter" && !e.shiftKey) {
                                        e.preventDefault();
                                        submitTextEdit(msg);
                                      }
                                    }}
                                  />
                                  <div className="inline-edit-actions">
                                    <button
                                      className="inline-edit-btn"
                                      onClick={() => submitTextEdit(msg)}
                                      disabled={loading || !editingTextValue.trim()}
                                      title="Save changes"
                                    >
                                      Save
                                    </button>
                                    <button
                                      className="inline-cancel-btn"
                                      onClick={cancelTextEdit}
                                      disabled={loading}
                                      title="Cancel"
                                    >
                                      Cancel
                                    </button>
                                  </div>
                                </div>
                              ) : (
                                <>
                                  <p className="message-text">{msg.content}</p>
                                  <button
                                    className="text-edit-icon-btn"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      startTextEdit(msg);
                                    }}
                                    disabled={loading}
                                    title="Edit this input"
                                  >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                      <path d="M12 20h9"/>
                                      <path d="M16.5 3.5a2.121 2.121 0 113 3L7 19l-4 1 1-4 12.5-12.5z"/>
                                    </svg>
                                  </button>
                                  <button
                                    className="text-retry-icon-btn"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleRetryRequest(msg);
                                    }}
                                    disabled={loading}
                                    title="Retry this request"
                                  >
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                      <path d="M23 4v6h-6"/>
                                      <path d="M1 20v-6h6"/>
                                      <path d="M3.51 9a9 9 0 0114.13-3.36L23 10"/>
                                      <path d="M20.49 15a9 9 0 01-14.13 3.36L1 14"/>
                                    </svg>
                                  </button>
                                </>
                              )}
                            </div>
                            {renderGeneratedStatus(msg)}
                          </>
                        ) : (
                          <p className="message-text assistant-status-text">
                            {retryingAssistantId === msg.id ? (
                              <span className="assistant-status-inline">
                                <svg className="assistant-status-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M21 12a9 9 0 00-9-9"/>
                                  <path d="M3 12a9 9 0 009 9" opacity="0.35"/>
                                </svg>
                                Regenerating lyrics...
                              </span>
                            ) : msg.emotion?.meta?.is_error ? (
                              msg.emotion?.meta?.description || msg.content || "Invalid input"
                            ) : regeneratedAssistantIds[msg.id] ? (
                              'Lyrics regenerated successfully ✓'
                            ) : (
                              'Lyrics generated successfully ✓'
                            )}
                          </p>
                        )}
                      </>
                    )}
                  </div>
                </div>
              );
            })}

            {pendingUserMessage && (
              <div className="message user" style={{ cursor: "default" }}>
                <div className="message-avatar">
                  <span>{pendingRequestNum}</span>
                </div>
                <div className="message-content">
                  {pendingUserMessage.input_type === "image" ? (
                    <>
                      <div className="message-image">
                        <img src={pendingUserMessage.image_preview} alt="Uploaded" />
                      </div>
                      <p className="message-text assistant-status-text user-generated-status">
                        <span className="assistant-status-inline">
                          <svg className="assistant-status-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 12a9 9 0 00-9-9"/>
                            <path d="M3 12a9 9 0 009 9" opacity="0.35"/>
                          </svg>
                          Analyzing image...
                        </span>
                      </p>
                    </>
                  ) : (
                    <>
                      <div className="user-text-bubble">
                        <p className="message-text">{pendingUserMessage.content}</p>
                      </div>
                      <p className="message-text assistant-status-text user-generated-status">
                        <span className="assistant-status-inline">
                          <svg className="assistant-status-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 12a9 9 0 00-9-9"/>
                            <path d="M3 12a9 9 0 009 9" opacity="0.35"/>
                          </svg>
                          Analyzing text...
                        </span>
                      </p>
                    </>
                  )}
                </div>
              </div>
            )}

            {loading && !retryContext && !pendingUserMessage && (
              <div className="message assistant">
                <div className="message-avatar">
                  <span>𝄞</span>
                </div>
                <div className="message-content">
                  <div className="loading-message">
                    <div className="loading-dots">
                      <span className="dot"></span>
                      <span className="dot"></span>
                      <span className="dot"></span>
                    </div>
                    <span className="loading-text">
                      {inputMode === 'image' ? 'Analyzing image...' : 'Analyzing text...'}
                    </span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <div className="chat-input-container">
        {inputMode === "text" && (
          <div className="chat-input-wrapper">
            <textarea
              ref={textareaRef}
              className="chat-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message LyricMind..."
              maxLength={maxTextLength}
              rows={1}
              disabled={loading}
            />
            <button
              className="media-button"
              onClick={() => handleModeSwitch("image")}
              disabled={loading}
              title="Upload image"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
            </button>
            <button
              className="send-button"
              onClick={handleAnalyze}
              disabled={!text.trim() || loading}
            >
              {loading ? (
                <svg className="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/>
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
              )}
            </button>
          </div>
        )}

        {inputMode === "image" && (
          <div className="image-input-wrapper">
            <div className="image-mode-header">
              <button
                className="image-mode-back-btn"
                onClick={() => handleModeSwitch("text")}
                disabled={loading}
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M15 18l-6-6 6-6"/>
                </svg>
                Text
              </button>
            </div>
            {!imagePreview ? (
              <div className="image-upload-area">
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  style={{ display: "none" }}
                  disabled={loading}
                />
                <div className="upload-buttons-group">
                  <button
                    className="upload-button"
                    onClick={() => fileInputRef.current?.click()}
                    disabled={loading}
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
                    </svg>
                    <span>Browse Files</span>
                  </button>
                  <button
                    className="upload-button camera-button"
                    onClick={handleCameraOpen}
                    disabled={loading}
                  >
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/>
                      <circle cx="12" cy="13" r="4"/>
                    </svg>
                    <span>Take Photo</span>
                  </button>
                </div>
                <span className="upload-hint">Max 10MB • JPG, PNG, GIF</span>
              </div>
            ) : (
              <div className="image-preview-container">
                <div className="image-preview">
                  <img src={imagePreview} alt="Selected" />
                  <button
                    className="remove-image-btn"
                    onClick={handleRemoveImage}
                    disabled={loading}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 6L6 18M6 6l12 12"/>
                    </svg>
                  </button>
                </div>
                <button
                  className="send-button"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? (
                    <svg className="spinner" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10"/>
                    </svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/>
                    </svg>
                  )}
                  Analyze Image
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
