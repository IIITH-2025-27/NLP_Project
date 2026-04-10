import { useState, useRef, useEffect } from "react";
import { useAnalysis } from "../hooks/useAnalysis";
import { useAuth } from "../context/AuthContext";
import apiService from "../services/api.service";
import DashboardSidebar from "../components/dashboard/DashboardSidebar";
import DashboardChatSection from "../components/dashboard/DashboardChatSection";
import DashboardLyricsPanel from "../components/dashboard/DashboardLyricsPanel";
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
  const [cameraTarget, setCameraTarget] = useState("main");
  const [preprocessedModalOpen, setPreprocessedModalOpen] = useState(false);
  const [preprocessedImageToShow, setPreprocessedImageToShow] = useState(null);
  const [pendingUserMessage, setPendingUserMessage] = useState(null);
  const [submittedImagePreview, setSubmittedImagePreview] = useState(null);
  const [retryContext, setRetryContext] = useState(null);
  const [retryingAssistantId, setRetryingAssistantId] = useState(null);
  const [regeneratedAssistantIds, setRegeneratedAssistantIds] = useState({});
  const [imageEditModalOpen, setImageEditModalOpen] = useState(false);
  const [editingImageMessage, setEditingImageMessage] = useState(null);
  const [editImageFile, setEditImageFile] = useState(null);
  const [editImagePreview, setEditImagePreview] = useState(null);
  const [errorToast, setErrorToast] = useState("");
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageEditFileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const requestRefs = useRef({});
  const pendingRetryRef = useRef(null);
  const retryInFlightRef = useRef(false);
  const userSelectionScrollRef = useRef(false);
  const retryImagePreviewRef = useRef(null);
  const processedResultRef = useRef(null);
  const toastTimerRef = useRef(null);

  const getErrorMessage = (error, fallback = "Something went wrong. Please try again.") => {
    if (!error) return fallback;
    if (typeof error === "string") return error;
    return error.message || fallback;
  };

  const showErrorToast = (message) => {
    setErrorToast(message || "Something went wrong. Please try again.");

    if (toastTimerRef.current) {
      clearTimeout(toastTimerRef.current);
    }

    toastTimerRef.current = setTimeout(() => {
      setErrorToast("");
      toastTimerRef.current = null;
    }, 3000);
  };

  useEffect(() => {
    return () => {
      if (toastTimerRef.current) {
        clearTimeout(toastTimerRef.current);
      }
    };
  }, []);

  const scrollToBottom = (behavior = "auto") => {
    requestAnimationFrame(() => {
      messagesEndRef.current?.scrollIntoView({ behavior, block: "end" });
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior, block: "end" });
      }, 60);
    });
  };

  const { user, logout } = useAuth();
  const { analyze, analyzeImage, loading, result, reset } = useAnalysis();

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
      showErrorToast(getErrorMessage(err, "Failed to load chats."));
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
      showErrorToast(getErrorMessage(err, "Failed to load messages."));
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
      showErrorToast(getErrorMessage(err, "Failed to create new chat."));
    }
  };

  // Get current chat  
  const currentChat = chats.find(chat => chat.id === currentChatId);
  const currentMessages = messages;

  // Handle analysis result
  useEffect(() => {
    if (result) {
      if (processedResultRef.current === result) {
        return;
      }
      processedResultRef.current = result;

      const saveMessages = async () => {
        try {
          const activeRetry = pendingRetryRef.current;

          // Retry flow: update existing user request in place
          if (activeRetry?.userMessageId) {
            const existingUserMessage = messages.find(m => m.id === activeRetry.userMessageId);

            const userMessageData = {
              content:
                result.input_text ||
                existingUserMessage?.content ||
                `[Image: ${result.input_filename || "uploaded"}]`,
              input_type: result.input_type || existingUserMessage?.input_type,
            };

            if (userMessageData.input_type === "image") {
              userMessageData.image_preview =
                retryImagePreviewRef.current || existingUserMessage?.image_preview;
            }
            if (result.emotion_detection.preprocessed_image) {
              userMessageData.preprocessed_image = result.emotion_detection.preprocessed_image;
            }

            const updatePayload = {
              content: userMessageData.content,
              input_type: userMessageData.input_type,
              emotion: result.emotion_detection,
              lyrics: result.lyric_generation.lyrics,
            };

            if (result.emotion_detection.preprocessed_image) {
              updatePayload.preprocessed_image = result.emotion_detection.preprocessed_image;
            }
            if (userMessageData.input_type === "image" && userMessageData.image_preview) {
              updatePayload.image_preview = userMessageData.image_preview;
            }

            const updatedUserMessage = await apiService.updateMessage(
              activeRetry.userMessageId,
              updatePayload
            );

            setMessages(prev =>
              prev.map(msg => (msg.id === updatedUserMessage.id ? updatedUserMessage : msg))
            );

            const requestMessages = messages
              .map(msg => (msg.id === updatedUserMessage.id ? updatedUserMessage : msg))
              .filter(msg => Boolean(msg.lyrics));

            const updatedAssistantIndex = requestMessages.findIndex(
              msg => msg.id === updatedUserMessage.id
            );
            if (updatedAssistantIndex !== -1) {
              setSelectedRequestIndex(updatedAssistantIndex);
            }

            setRetryingAssistantId(null);
            setRegeneratedAssistantIds(prev => ({
              ...prev,
              [updatedUserMessage.id]: true,
            }));
            pendingRetryRef.current = null;
            retryInFlightRef.current = false;
            retryImagePreviewRef.current = null;
            setRetryContext(null);
            setText("");
            return;
          }

          // Create a chat if none exists
          let chatId = currentChatId;
          if (!chatId) {
            const newChat = await apiService.createChat("New Chat");
            setChats(prev => [newChat, ...prev]);
            setCurrentChatId(newChat.id);
            chatId = newChat.id;
          }
          
          // Create user message
          const resolvedInputType = result.input_type || 'text';
          const userMessageData = {
            content: result.input_text || `[Image: ${result.input_filename || 'uploaded'}]`,
            message_type: 'user',
            input_type: resolvedInputType,
          };
          
          if (resolvedInputType === 'image' && (submittedImagePreview || imagePreview)) {
            userMessageData.image_preview = submittedImagePreview || imagePreview;
          }
          
          const userMessage = await apiService.createMessage(chatId, userMessageData);

          const updatePayload = {
            content: userMessageData.content,
            input_type: resolvedInputType,
            emotion: result.emotion_detection,
            lyrics: result.lyric_generation.lyrics,
          };
          if (result.emotion_detection.preprocessed_image) {
            updatePayload.preprocessed_image = result.emotion_detection.preprocessed_image;
          }
          if (resolvedInputType === 'image' && userMessageData.image_preview) {
            updatePayload.image_preview = userMessageData.image_preview;
          }

          const updatedUserMessage = await apiService.updateMessage(userMessage.id, updatePayload);
          
          // Update local messages state
          setMessages(prev => [...prev, updatedUserMessage]);
          
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
          const requestMessages = [...messages, updatedUserMessage].filter(m => Boolean(m.lyrics));
          setSelectedRequestIndex(requestMessages.length - 1);
          
          setText("");
          handleRemoveImage();
          setPendingUserMessage(null);
          setSubmittedImagePreview(null);
          setRetryContext(null);
          setRetryingAssistantId(null);
          retryInFlightRef.current = false;
          retryImagePreviewRef.current = null;
        } catch (err) {
          console.error("Failed to save messages:", err);
          showErrorToast(getErrorMessage(err, "Failed to save messages."));
          setPendingUserMessage(null);
          setSubmittedImagePreview(null);
          pendingRetryRef.current = null;
          retryInFlightRef.current = false;
          retryImagePreviewRef.current = null;
          setRetryingAssistantId(null);
          setRetryContext(null);
          processedResultRef.current = null;
        }
      };
      
      saveMessages();
    }
  }, [result]);

  // Auto-scroll to bottom only when message count changes
  useEffect(() => {
    scrollToBottom("smooth");
  }, [currentMessages.length]);

  // Keep newest pending image + loader visible without manual scrolling (except in-place retry/edit)
  useEffect(() => {
    if ((loading || pendingUserMessage) && !retryContext) {
      scrollToBottom("auto");
    }
  }, [loading, pendingUserMessage, retryContext, currentChatId, currentMessages.length]);

  // Auto-select latest request when chat changes or messages load
  useEffect(() => {
    const requestMessages = currentMessages.filter(msg => Boolean(msg.lyrics));
    if (requestMessages.length > 0 && selectedRequestIndex === null) {
      setSelectedRequestIndex(requestMessages.length - 1);
    }
  }, [currentChatId, currentMessages, selectedRequestIndex]);

  const handleAnalyze = async () => {
    if (inputMode === "text") {
      if (!text.trim() || loading) return;
      const currentText = text.trim();

      setPendingUserMessage({
        id: `pending-text-${Date.now()}`,
        input_type: "text",
        content: currentText,
        message_type: "user",
      });
      setText("");
      scrollToBottom("auto");

      try {
        await analyze(currentText);
      } catch (err) {
        setPendingUserMessage(null);
        showErrorToast(getErrorMessage(err, "Failed to generate lyrics."));
      }
    } else if (inputMode === "image") {
      if (!selectedImage || loading) return;
      const currentPreview = imagePreview;
      const currentImage = selectedImage;

      if (currentPreview) {
        setSubmittedImagePreview(currentPreview);
        setPendingUserMessage({
          id: `pending-image-${Date.now()}`,
          input_type: "image",
          image_preview: currentPreview,
          message_type: "user",
        });
      }

      // Close large image input box immediately
      handleRemoveImage();
      setInputMode("text");
      scrollToBottom("auto");

      try {
        await analyzeImage(currentImage);
      } catch (err) {
        showErrorToast(getErrorMessage(err, "Failed to analyze image."));
        try {
          // Persist failed image request so preview remains visible in chat history
          let chatId = currentChatId;
          if (!chatId) {
            const newChat = await apiService.createChat("New Chat");
            setChats(prev => [newChat, ...prev]);
            setCurrentChatId(newChat.id);
            chatId = newChat.id;
          }

          const fallbackError = err?.message || "Failed to analyze image";
          const userMessageData = {
            content: `[Image: ${currentImage?.name || "uploaded"}]`,
            message_type: "user",
            input_type: "image",
            image_preview: currentPreview,
          };

          const userMessage = await apiService.createMessage(chatId, userMessageData);

          const errorUpdatePayload = {
            content: userMessageData.content,
            input_type: "image",
            emotion: {
              emotion: "Invalid input",
              confidence: 0,
              meta: {
                emoji: "⚠️",
                description: fallbackError,
                is_error: true,
              },
            },
            lyrics: "Invalid input",
          };

          const updatedUserMessage = await apiService.updateMessage(userMessage.id, errorUpdatePayload);

          setMessages(prev => [...prev, updatedUserMessage]);

          const requestMessages = [...messages, updatedUserMessage].filter(
            message => Boolean(message.lyrics)
          );
          setSelectedRequestIndex(requestMessages.length - 1);

          const chat = chats.find(c => c.id === chatId);
          if (!chat || chat.title === "New Chat") {
            const displayContent = userMessageData.content;
            await apiService.updateChat(chatId, { title: displayContent });
            setChats(prev => prev.map(chatItem =>
              chatItem.id === chatId ? { ...chatItem, title: displayContent } : chatItem
            ));
          }

          reset();
        } catch (saveErr) {
          console.error("Failed to save failed image request:", saveErr);
          showErrorToast(getErrorMessage(saveErr, "Failed to save failed image request."));
        } finally {
          setPendingUserMessage(null);
          setSubmittedImagePreview(null);
        }
      }
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
      showErrorToast("Unable to access camera. Please check permissions.");
      setCameraModalOpen(false);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
  };

  const handleCameraOpen = (target = "main") => {
    setCameraTarget(target);
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
          const capturedPreview = canvas.toDataURL('image/jpeg');

          if (cameraTarget === "edit") {
            setEditImageFile(file);
            setEditImagePreview(capturedPreview);
          } else {
            setSelectedImage(file);
            setImagePreview(capturedPreview);
          }

          handleCameraClose();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  const handleCameraClose = () => {
    stopCamera();
    setCameraModalOpen(false);
    setCameraTarget("main");
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
    setMessages([]);
    setSelectedRequestIndex(null);
    setRetryingAssistantId(null);
    setRegeneratedAssistantIds({});
    setPendingUserMessage(null);
    setSubmittedImagePreview(null);
    pendingRetryRef.current = null;
    retryInFlightRef.current = false;
    await loadMessages(chatId);
    reset();
    setText("");
    setInputMode("text");
    handleRemoveImage();
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
      showErrorToast(getErrorMessage(err, "Failed to delete chat."));
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

  // Get requests (messages that have generated lyrics) from current chat
  const requests = currentMessages.filter(msg => Boolean(msg.lyrics));
  const pendingRequestNum = requests.length + 1;
  
  // Get selected request data
  const selectedRequest = selectedRequestIndex !== null && requests[selectedRequestIndex] 
    ? requests[selectedRequestIndex] 
    : null;

  // Helper function to get request number for user messages
  const getUserRequestNumber = (userMsgIndex) => {
    const currentMessage = currentMessages[userMsgIndex];
    if (currentMessage?.lyrics) {
      const requestIndex = requests.findIndex(req => req.id === currentMessage.id);
      return requestIndex !== -1 ? requestIndex + 1 : null;
    }

    for (let i = userMsgIndex + 1; i < currentMessages.length; i++) {
      if (currentMessages[i].lyrics) {
        const requestIndex = requests.findIndex(req => req.id === currentMessages[i].id);
        return requestIndex !== -1 ? requestIndex + 1 : null;
      }
    }
    return null;
  };

  const handleMessageSelect = (message, messageIndex) => {
    if (message.lyrics) {
      const requestIndex = requests.findIndex(req => req.id === message.id);
      if (requestIndex !== -1) {
        userSelectionScrollRef.current = true;
        setSelectedRequestIndex(requestIndex);
      }
      return;
    }

    // For non-request messages, select the next generated request if available
    for (let i = messageIndex + 1; i < currentMessages.length; i++) {
      if (currentMessages[i].lyrics) {
        const requestIndex = requests.findIndex(req => req.id === currentMessages[i].id);
        if (requestIndex !== -1) {
          userSelectionScrollRef.current = true;
          setSelectedRequestIndex(requestIndex);
        }
        break;
      }
    }
  };

  const handleRequestDropdownChange = (value) => {
    if (value === '') {
      setSelectedRequestIndex(null);
      return;
    }
    userSelectionScrollRef.current = true;
    setSelectedRequestIndex(parseInt(value));
  };

  const dataUrlToFile = (dataUrl, fileName = "retry-image.jpg") => {
    const parts = dataUrl.split(",");
    if (parts.length !== 2) {
      throw new Error("Invalid image preview format");
    }

    const mimeMatch = parts[0].match(/data:(.*?);base64/);
    const mimeType = mimeMatch ? mimeMatch[1] : "image/jpeg";
    const byteString = atob(parts[1]);
    const byteArray = new Uint8Array(byteString.length);

    for (let i = 0; i < byteString.length; i++) {
      byteArray[i] = byteString.charCodeAt(i);
    }

    return new File([byteArray], fileName, { type: mimeType });
  };

  const resetRetryFlowState = () => {
    pendingRetryRef.current = null;
    retryInFlightRef.current = false;
    retryImagePreviewRef.current = null;
    setRetryContext(null);
    setRetryingAssistantId(null);
  };

  const prepareRequestRegeneration = (message) => {
    const targetMessage = currentMessages.find(msg => msg.id === message.id);
    if (!targetMessage) {
      alert("Unable to edit this request.");
      return null;
    }

    if (!targetMessage.lyrics) {
      alert("No generated lyrics found for this input.");
      return null;
    }

    const nextRetryContext = {
      userMessageId: message.id,
    };

    pendingRetryRef.current = nextRetryContext;
    retryInFlightRef.current = true;
    setRetryContext(nextRetryContext);
    setRetryingAssistantId(message.id);
    setRegeneratedAssistantIds(prev => {
      const next = { ...prev };
      delete next[message.id];
      return next;
    });

    return nextRetryContext;
  };

  const handleRetryRequest = async (message) => {
    if (loading || retryInFlightRef.current) return;

    try {
      if (!prepareRequestRegeneration(message)) {
        return;
      }

      if (message.input_type === "image") {
        if (!message.image_preview) {
          alert("Image preview not available for retry.");
          resetRetryFlowState();
          return;
        }

        const imageFile = dataUrlToFile(message.image_preview, `retry-${message.id}.jpg`);
        retryImagePreviewRef.current = message.image_preview;
        await analyzeImage(imageFile);
        return;
      }

      const retryText = (message.content || "").trim();
      if (!retryText) {
        resetRetryFlowState();
        return;
      }

      await analyze(retryText);
    } catch (err) {
      console.error("Retry failed:", err);
      resetRetryFlowState();
      showErrorToast(getErrorMessage(err, "Failed to retry this request. Please try again."));
    }
  };

  const handleEditTextRequest = async (message, updatedText) => {
    if (loading || retryInFlightRef.current) return;

    const nextText = (updatedText || "").trim();
    if (!nextText) {
      alert("Text cannot be empty.");
      return;
    }

    try {
      if (!prepareRequestRegeneration(message)) {
        return;
      }

      setInputMode("text");
      setText(nextText);
      await analyze(nextText);
    } catch (err) {
      console.error("Edit text request failed:", err);
      resetRetryFlowState();
      showErrorToast(getErrorMessage(err, "Failed to update this request. Please try again."));
    }
  };

  const openImageEditModal = (message) => {
    if (loading || retryInFlightRef.current) return;
    if (!message?.image_preview) {
      alert("Image preview not available for edit.");
      return;
    }

    setEditingImageMessage(message);
    setEditImagePreview(message.image_preview);
    setEditImageFile(null);
    setImageEditModalOpen(true);
  };

  const closeImageEditModal = () => {
    setImageEditModalOpen(false);
    setEditingImageMessage(null);
    setEditImageFile(null);
    setEditImagePreview(null);
    if (imageEditFileInputRef.current) {
      imageEditFileInputRef.current.value = "";
    }
  };

  const handleImageEditSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 10 * 1024 * 1024) {
      alert("Image size must be less than 10MB");
      return;
    }

    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image file");
      return;
    }

    setEditImageFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setEditImagePreview(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmitImageEdit = async () => {
    if (!editingImageMessage || !editImageFile || loading || retryInFlightRef.current) return;

    try {
      if (!prepareRequestRegeneration(editingImageMessage)) {
        return;
      }

      retryImagePreviewRef.current = editImagePreview || editingImageMessage.image_preview;
      closeImageEditModal();
      await analyzeImage(editImageFile);
    } catch (err) {
      console.error("Edit image request failed:", err);
      resetRetryFlowState();
      showErrorToast(getErrorMessage(err, "Failed to update this image request. Please try again."));
    }
  };

  // Scroll to selected request message when it changes
  useEffect(() => {
    if (!userSelectionScrollRef.current) return;
    if (loading || pendingUserMessage) return;

    if (selectedRequestIndex !== null) {
      const selectedRequestMsg = requests[selectedRequestIndex];
      if (selectedRequestMsg) {
        const element = requestRefs.current[selectedRequestMsg.id];
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }
    userSelectionScrollRef.current = false;
  }, [selectedRequestIndex, requests, currentMessages, loading, pendingUserMessage]);

  return (
    <div className="chat-layout" onClick={handleOverlayClick}>
      {errorToast && (
        <div className="dashboard-error-toast" role="alert" aria-live="assertive">
          <span className="dashboard-error-toast__icon">⚠</span>
          <span className="dashboard-error-toast__message">{errorToast}</span>
          <button
            className="dashboard-error-toast__close"
            onClick={() => setErrorToast("")}
            aria-label="Close error notification"
          >
            ×
          </button>
        </div>
      )}

      <DashboardSidebar
        sidebarOpen={sidebarOpen}
        handleNewChat={handleNewChat}
        loadingChats={loadingChats}
        chatList={chatList}
        currentChatId={currentChatId}
        handleChatSelect={handleChatSelect}
        handleDeleteChat={handleDeleteChat}
        user={user}
        logout={logout}
      />

      <div className="split-container">
        <DashboardChatSection
          loadingChats={loadingChats}
          loadingMessages={loadingMessages}
          currentMessages={currentMessages}
          examplePrompts={examplePrompts}
          setText={setText}
          requestRefs={requestRefs}
          user={user}
          getUserRequestNumber={getUserRequestNumber}
          handleMessageSelect={handleMessageSelect}
          setPreprocessedImageToShow={setPreprocessedImageToShow}
          setPreprocessedModalOpen={setPreprocessedModalOpen}
          handleRetryRequest={handleRetryRequest}
          loading={loading}
          retryingAssistantId={retryingAssistantId}
          regeneratedAssistantIds={regeneratedAssistantIds}
          pendingUserMessage={pendingUserMessage}
          pendingRequestNum={pendingRequestNum}
          retryContext={retryContext}
          inputMode={inputMode}
          messagesEndRef={messagesEndRef}
          sidebarOpen={sidebarOpen}
          setSidebarOpen={setSidebarOpen}
          handleModeSwitch={handleModeSwitch}
          textareaRef={textareaRef}
          text={text}
          maxTextLength={MAX_TEXT_LENGTH}
          handleKeyDown={handleKeyDown}
          handleAnalyze={handleAnalyze}
          imagePreview={imagePreview}
          fileInputRef={fileInputRef}
          handleImageSelect={handleImageSelect}
          handleCameraOpen={handleCameraOpen}
          handleRemoveImage={handleRemoveImage}
          handleEditTextRequest={handleEditTextRequest}
          openImageEditModal={openImageEditModal}
        />

        <DashboardLyricsPanel
          selectedRequestIndex={selectedRequestIndex}
          handleRequestDropdownChange={handleRequestDropdownChange}
          loadingMessages={loadingMessages}
          requests={requests}
          selectedRequest={selectedRequest}
        />
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

      {/* Image Edit Modal */}
      {imageEditModalOpen && (
        <div className="image-edit-modal-overlay" onClick={closeImageEditModal}>
          <div className="image-edit-modal" onClick={(e) => e.stopPropagation()}>
            <div className="image-edit-modal-header">
              <h3>Edit Image Input</h3>
              <button className="image-edit-close-btn" onClick={closeImageEditModal}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 6L6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
            <div className="image-edit-modal-body">
              <input
                ref={imageEditFileInputRef}
                type="file"
                accept="image/*"
                onChange={handleImageEditSelect}
                style={{ display: "none" }}
                disabled={loading}
              />
              <div className="image-edit-actions-row">
                <button
                  className="image-edit-upload-btn"
                  onClick={() => imageEditFileInputRef.current?.click()}
                  disabled={loading}
                >
                  Choose Image
                </button>
                <button
                  className="image-edit-upload-btn"
                  onClick={() => handleCameraOpen("edit")}
                  disabled={loading}
                >
                  Take Photo
                </button>
              </div>
              {editImagePreview && (
                <div className="image-edit-preview">
                  <img src={editImagePreview} alt="Edited input preview" />
                </div>
              )}
            </div>
            <div className="image-edit-modal-footer">
              <button className="image-edit-cancel-btn" onClick={closeImageEditModal} disabled={loading}>
                Cancel
              </button>
              <button
                className="image-edit-save-btn"
                onClick={handleSubmitImageEdit}
                disabled={!editImageFile || loading}
              >
                Analyze Image
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
