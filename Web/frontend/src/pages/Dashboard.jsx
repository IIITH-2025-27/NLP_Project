import { useState, useRef, useEffect } from "react";
import { useAnalysis } from "../hooks/useAnalysis";
import { useAuth } from "../context/AuthContext";
import apiService from "../services/api.service";
import LyricsCard from "../components/lyrics/LyricsCard";
import { MAX_TEXT_LENGTH } from "../utils/constants";
import "../assets/styles/dashboard.css";

export default function Dashboard() {
  const [text, setText] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [loadingChats, setLoadingChats] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [selectedRequestIndex, setSelectedRequestIndex] = useState(null);
  const [inputMode, setInputMode] = useState("text"); // "text" or "image"
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [cameraModalOpen, setCameraModalOpen] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [preprocessedModalOpen, setPreprocessedModalOpen] = useState(false);
  const [preprocessedImageToShow, setPreprocessedImageToShow] = useState(null);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const requestRefs = useRef({});

  const { user, logout } = useAuth();
  const { analyze, analyzeImage, loading, result, error, reset } = useAnalysis();

  // Load chats from API on mount or when user changes
  useEffect(() => {
    if (!user?.id) return;
    
    loadChats();
    
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const loadChats = async () => {
    try {
      setLoadingChats(true);
      const data = await apiService.getChats();
      setChats(data.chats || []);
      
      // If there are chats, select the first (most recent) one
      if (data.chats && data.chats.length > 0) {
        const firstChatId = data.chats[0].id;
        setCurrentChatId(firstChatId);
        await loadMessages(firstChatId);
      } else {
        // No chats - user will create one when they send first message
        setCurrentChatId(null);
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to load chats:", err);
    } finally {
      setLoadingChats(false);
    }
  };

  // Load messages for a specific chat
  const loadMessages = async (chatId) => {
    try {
      setLoadingMessages(true);
      const data = await apiService.getMessages(chatId);
      setMessages(data.messages || []);
    } catch (err) {
      console.error("Failed to load messages:", err);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  // Create a new chat session
  const createNewChat = async () => {
    try {
      const newChat = await apiService.createChat("New Chat");
      setChats(prev => [newChat, ...prev]);
      setCurrentChatId(newChat.id);
      setMessages([]);
      reset();
      setText("");
      setInputMode("text");
      handleRemoveImage();
      setSelectedRequestIndex(null);
      return newChat;
    } catch (err) {
      console.error("Failed to create new chat:", err);
    }
  };

  // Get current chat  
  const currentChat = chats.find(chat => chat.id === currentChatId);
  const currentMessages = messages;

  // Handle analysis result
  useEffect(() => {
    if (result) {
      const saveMessages = async () => {
        try {
          // Create a chat if none exists
          let chatId = currentChatId;
          if (!chatId) {
            const newChat = await apiService.createChat("New Chat");
            setChats(prev => [newChat, ...prev]);
            setCurrentChatId(newChat.id);
            chatId = newChat.id;
          }
          
          // Create user message
          const userMessageData = {
            content: result.input_text || `[Image: ${result.input_filename || 'uploaded'}]`,
            message_type: 'user',
          };
          
          // Add optional fields only if they have values
          if (result.input_type) {
            userMessageData.input_type = result.input_type;
          }
          if (result.input_type === 'image' && imagePreview) {
            userMessageData.image_preview = imagePreview;
          }
          // Store preprocessed image in user message for later viewing
          if (result.emotion_detection.preprocessed_image) {
            userMessageData.preprocessed_image = result.emotion_detection.preprocessed_image;
          }
          
          const userMessage = await apiService.createMessage(chatId, userMessageData);
          
          // Create assistant message
          const assistantMessageData = {
            content: result.lyric_generation.lyrics,
            message_type: 'assistant',
            emotion: result.emotion_detection,
            lyrics: result.lyric_generation.lyrics
          };
          
          // Add preprocessed image if available
          if (result.emotion_detection.preprocessed_image) {
            assistantMessageData.preprocessed_image = result.emotion_detection.preprocessed_image;
          }
          
          const assistantMessage = await apiService.createMessage(chatId, assistantMessageData);
          
          // Update local messages state
          setMessages(prev => [...prev, userMessage, assistantMessage]);
          
          // Update chat title with first user message
          const chat = chats.find(c => c.id === chatId);
          if (!chat || chat.title === "New Chat") {
            const displayContent = userMessageData.input_type === 'image' 
              ? userMessageData.content 
              : userMessageData.content.slice(0, 50) + (userMessageData.content.length > 50 ? "..." : "");
            
            await apiService.updateChat(chatId, { title: displayContent });
            setChats(prev => prev.map(chat => 
              chat.id === chatId ? { ...chat, title: displayContent } : chat
            ));
          }
          
          // Auto-select the latest request
          const assistantMessages = [...messages, userMessage, assistantMessage].filter(m => m.message_type === 'assistant');
          setSelectedRequestIndex(assistantMessages.length - 1);
          
          setText("");
          handleRemoveImage();
        } catch (err) {
          console.error("Failed to save messages:", err);
        }
      };
      
      saveMessages();
    }
  }, [result]);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentMessages]);

  // Auto-select latest request when chat changes or messages load
  useEffect(() => {
    const assistantMessages = currentMessages.filter(msg => msg.message_type === 'assistant');
    if (assistantMessages.length > 0 && selectedRequestIndex === null) {
      setSelectedRequestIndex(assistantMessages.length - 1);
    }
  }, [currentChatId, currentMessages, selectedRequestIndex]);

  const handleAnalyze = async () => {
    if (inputMode === "text") {
      if (!text.trim() || loading) return;
      await analyze(text);
    } else if (inputMode === "image") {
      if (!selectedImage || loading) return;
      await analyzeImage(selectedImage);
    }
  };

  const handleImageSelect = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file size (10MB max)
      if (file.size > 10 * 1024 * 1024) {
        alert("Image size must be less than 10MB");
        return;
      }

      // Validate file type
      if (!file.type.startsWith("image/")) {
        alert("Please select a valid image file");
        return;
      }

      setSelectedImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Camera functions
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" },
        audio: false 
      });
      setCameraStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      alert("Unable to access camera. Please check permissions.");
      setCameraModalOpen(false);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
  };

  const handleCameraOpen = () => {
    setCameraModalOpen(true);
  };

  const handleCameraCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;
      
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "camera-photo.jpg", { type: "image/jpeg" });
          setSelectedImage(file);
          setImagePreview(canvas.toDataURL('image/jpeg'));
          handleCameraClose();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const handleCameraClose = () => {
    stopCamera();
    setCameraModalOpen(false);
  };

  // Start camera when modal opens
  useEffect(() => {
    if (cameraModalOpen) {
      startCamera();
    }
    return () => {
      if (cameraModalOpen) {
        stopCamera();
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cameraModalOpen]);

  const handleModeSwitch = (mode) => {
    if (mode !== inputMode) {
      setInputMode(mode);
      setText("");
      handleRemoveImage();
    }
  };

  const handleNewChat = () => {
    // If current chat is already empty "New Chat", don't create another
    if (currentChat && currentChat.title === "New Chat" && messages.length === 0) {
      return; // Already on an empty new chat
    }
    
    // Create a new chat
    createNewChat();
  };

  // Switch to a different chat
  const handleChatSelect = async (chatId) => {
    setCurrentChatId(chatId);
    await loadMessages(chatId);
    reset();
    setText("");
    setInputMode("text");
    handleRemoveImage();
    setSelectedRequestIndex(null);
  };

  // Delete a chat
  const handleDeleteChat = async (chatId) => {
    try {
      await apiService.deleteChat(chatId);
      
      // Remove from local state
      setChats(prev => prev.filter(c => c.id !== chatId));

      // If deleting current chat, switch to another or create new
      if (chatId === currentChatId) {
        const remainingChats = chats.filter(c => c.id !== chatId);
        if (remainingChats.length > 0) {
          const nextChatId = remainingChats[0].id;
          setCurrentChatId(nextChatId);
          await loadMessages(nextChatId);
        } else {
          await createNewChat();
        }
      }
    } catch (err) {
      console.error('Error deleting chat:', err);
    }
  };

  // Get sorted chat list (most recent first)
  const chatList = [...chats].sort((a, b) => 
    new Date(b.updatedAt) - new Date(a.updatedAt)
  );

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAnalyze();
    }
  };

  // Close sidebar on mobile when clicking outside
  const handleOverlayClick = (e) => {
    if (e.target.classList.contains('chat-layout') && !sidebarOpen) {
      return;
    }
    if (window.innerWidth <= 768 && !sidebarOpen === false) {
      const sidebar = document.querySelector('.chat-sidebar');
      if (sidebar && !sidebar.contains(e.target) && !e.target.closest('.sidebar-toggle')) {
        setSidebarOpen(false);
      }
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px';
    }
  }, [text]);

  const examplePrompts = [
    { emoji: "😊", text: "I'm feeling so grateful and happy today!" },
    { emoji: "😢", text: "Missing someone special, feeling alone tonight" },
    { emoji: "😲", text: "I can't believe this happened! Totally unexpected!" },
    { emoji: "😠", text: "I'm so frustrated and angry about this situation" }
  ];

  // Get requests (assistant messages with lyrics) from current chat
  const requests = currentMessages.filter(msg => msg.message_type === 'assistant');
  
  // Get selected request data
  const selectedRequest = selectedRequestIndex !== null && requests[selectedRequestIndex] 
    ? requests[selectedRequestIndex] 
    : null;

  // Helper function to get request number for user messages
  const getUserRequestNumber = (userMsgIndex) => {
    // Find the next assistant message after this user message
    for (let i = userMsgIndex + 1; i < currentMessages.length; i++) {
      if (currentMessages[i].message_type === 'assistant') {
        const assistantIndex = requests.findIndex(req => req.id === currentMessages[i].id);
        return assistantIndex !== -1 ? assistantIndex + 1 : null;
      }
    }
    return null;
  };

  // Scroll to selected request's user message when it changes
  useEffect(() => {
    if (selectedRequestIndex !== null) {
      // Find the user message that precedes the selected assistant message
      const assistantMsg = requests[selectedRequestIndex];
      if (assistantMsg) {
        const assistantIdx = currentMessages.findIndex(msg => msg.id === assistantMsg.id);
        // Look backwards for the user message
        for (let i = assistantIdx - 1; i >= 0; i--) {
          if (currentMessages[i].message_type === 'user') {
            const element = requestRefs.current[currentMessages[i].id];
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
            break;
          }
        }
      }
    }
  }, [selectedRequestIndex, requests, currentMessages]);

  return (
    <div className="chat-layout" onClick={handleOverlayClick}>
      {/* Sidebar */}
      <aside className={`chat-sidebar ${sidebarOpen ? '' : 'closed'}`}>
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={handleNewChat}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            New chat
          </button>
        </div>

        <div className="sidebar-content">
          <div className="sidebar-section">
            <h3 className="sidebar-title">Recent Chats</h3>
            {chatList.length > 0 ? (
              <div className="history-items">
                {chatList.map(chat => (
                  <div 
                    key={chat.id} 
                    className={`history-item ${chat.id === currentChatId ? 'active' : ''}`}
                    onClick={() => handleChatSelect(chat.id)}
                  >
                    <div className="history-text">
                      {chat.title}
                    </div>
                    <button 
                      className="history-delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteChat(chat.id);
                      }}
                      title="Delete chat"
                    >
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="sidebar-empty">No chats yet</div>
            )}
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="user-menu">
            <div className="user-avatar-small">
              {user?.name?.charAt(0).toUpperCase() || "U"}
            </div>
            <span className="user-name-small">{user?.name}</span>
            <button className="logout-icon" onClick={logout} title="Logout">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9"/>
              </svg>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content - Split Layout */}
      <div className="split-container">
        {/* Left: Chat Section */}
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
            {currentMessages.length === 0 ? (
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
                      ref={(el) => requestRefs.current[msg.id] = el}
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
                          <div className="message-image">
                            <img src={msg.image_preview} alt="Uploaded" />
                            {msg.preprocessed_image && (
                              <button 
                                className="preprocessed-view-btn"
                                onClick={() => {
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
                          </div>
                        ) : (
                          <p className="message-text">
                            {msg.message_type === 'user' ? msg.content : 'Lyrics generated successfully ✓'}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
                
                {/* Loading indicator */}
                {loading && (
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
            {/* Mode Toggle */}
            <div className="input-mode-toggle">
              <button
                className={`mode-btn ${inputMode === "text" ? "active" : ""}`}
                onClick={() => handleModeSwitch("text")}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 7h16M4 12h16M4 17h10"/>
                </svg>
                Text
              </button>
              <button
                className={`mode-btn ${inputMode === "image" ? "active" : ""}`}
                onClick={() => handleModeSwitch("image")}
                disabled={loading}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <path d="M21 15l-5-5L5 21"/>
                </svg>
                Image
              </button>
            </div>

            {/* Text Input */}
            {inputMode === "text" && (
              <div className="chat-input-wrapper">
                <textarea
                  ref={textareaRef}
                  className="chat-input"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Message LyricMind..."
                  maxLength={MAX_TEXT_LENGTH}
                  rows={1}
                  disabled={loading}
                />
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

            {/* Image Input */}
            {inputMode === "image" && (
              <div className="image-input-wrapper">
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

            {error && <div className="input-error">{error}</div>}
          </div>
        </main>

        {/* Right: Lyrics Section */}
        <aside className="lyrics-panel">
          <div className="lyrics-panel-header">
            <label htmlFor="request-select" className="request-label">Select Request:</label>
            <select 
              id="request-select"
              className="request-dropdown"
              value={selectedRequestIndex !== null ? selectedRequestIndex : ''}
              onChange={(e) => setSelectedRequestIndex(e.target.value === '' ? null : parseInt(e.target.value))}
              disabled={requests.length === 0}
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
            {selectedRequest ? (
              <div className="lyrics-display">
                <div className="lyrics-emotion-compact">
                  <span className="lyrics-emoji">{selectedRequest.emotion.meta?.emoji || "❓"}</span>
                  <div className="lyrics-emotion-info">
                    <span className="lyrics-emotion-name">{selectedRequest.emotion.emotion}</span>
                    <span className="lyrics-emotion-desc">{selectedRequest.emotion.meta?.description || ""}</span>
                  </div>
                  <div className="lyrics-confidence-badge">
                    {Math.round(selectedRequest.emotion.confidence * 100)}%
                  </div>
                </div>
                <div className="lyrics-text-section">
                  <h3>Generated Lyrics</h3>
                  <LyricsCard 
                    lyrics={selectedRequest.lyrics}
                    emotion={selectedRequest.emotion.emotion}
                  />
                </div>
              </div>
            ) : (
              <div className="lyrics-empty">
                <div className="lyrics-empty-icon">🎵</div>
                <p>Select a request to view lyrics</p>
              </div>
            )}
          </div>
        </aside>
      </div>

      {/* Camera Modal */}
      {cameraModalOpen && (
        <div className="camera-modal-overlay" onClick={handleCameraClose}>
          <div className="camera-modal" onClick={(e) => e.stopPropagation()}>
            <div className="camera-modal-header">
              <h3>Take Photo</h3>
              <button className="camera-close-btn" onClick={handleCameraClose}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div className="camera-modal-body">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline
                className="camera-video"
              />
              <canvas ref={canvasRef} style={{ display: 'none' }} />
            </div>
            <div className="camera-modal-footer">
              <button className="camera-cancel-btn" onClick={handleCameraClose}>
                Cancel
              </button>
              <button className="camera-capture-btn" onClick={handleCameraCapture}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <circle cx="12" cy="12" r="10"/>
                </svg>
                Capture
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Preprocessed Image Modal */}
      {preprocessedModalOpen && preprocessedImageToShow && (
        <div className="preprocessed-modal-overlay" onClick={() => setPreprocessedModalOpen(false)}>
          <div className="preprocessed-modal" onClick={(e) => e.stopPropagation()}>
            <div className="preprocessed-modal-header">
              <h3>Detected Face (224×224)</h3>
              <button className="preprocessed-close-btn" onClick={() => setPreprocessedModalOpen(false)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div className="preprocessed-modal-body">
              <div className="preprocessed-display">
                <img src={preprocessedImageToShow} alt="Preprocessed face" />
              </div>
              <p className="preprocessed-modal-note">
                This is the 224×224 face image that was analyzed by the emotion detection model.
                The face was automatically detected, cropped, and resized to match the model's training data.
              </p>
            </div>
            <div className="preprocessed-modal-footer">
              <button className="preprocessed-ok-btn" onClick={() => setPreprocessedModalOpen(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
