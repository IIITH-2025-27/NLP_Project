# LyricMind Frontend Structure

## 📁 Folder Structure

```
frontend/
  src/
    assets/
      styles/           # Global and page-specific styles
        globals.css     # Global CSS variables and base styles
        auth.css        # Authentication page styles
        dashboard.css   # Dashboard page styles
    
    components/
      common/           # Reusable UI components
        Button.jsx
        Button.css
        Input.jsx
        Input.css
        Loader.jsx
        Loader.css
        ErrorMessage.jsx
        ErrorMessage.css
      
      layout/           # Layout components
        Header.jsx
        Header.css
        Footer.jsx
        Layout.jsx      # Main layout wrapper
      
      emotion/          # Emotion-related components
        EmotionBadge.jsx
        EmotionBadge.css
        EmotionScores.jsx
        EmotionScores.css
      
      lyrics/           # Lyrics-related components
        LyricsCard.jsx
        LyricsCard.css
      
      history/          # History-related components
        HistoryItem.jsx
        HistoryItem.css
        HistoryList.jsx
        HistoryList.css
    
    hooks/              # Custom React hooks
      useAnalysis.js    # Hook for text analysis (emotion → lyrics)
      useHistory.js     # Hook for managing user history
    
    services/           # API and business logic
      api.service.js    # Main API client
      auth.service.js   # Authentication service
      storage.service.js # LocalStorage management
    
    utils/              # Utility functions and constants
      constants.js      # App constants (colors, API URLs, etc.)
      helpers.js        # Helper functions
    
    context/
      AuthContext.jsx   # Authentication context provider
    
    pages/
      AuthPage.jsx      # Sign in / Sign up page
      Dashboard.jsx     # Main dashboard with analyze and history
    
    App.jsx             # Main app component
    main.jsx            # Entry point
```

## 🎨 Design System

### Colors
- **Primary**: `#6366f1` (Indigo)
- **Secondary**: `#8b5cf6` (Purple)
- **Danger**: `#ef4444` (Red)
- **Success**: `#10b981` (Green)
- **Background**: Dark theme with gradient

### Emotion Colors
- **Joy**: `#FFD93D` (Yellow)
- **Sadness**: `#6BA3BE` (Blue)
- **Anger**: `#FF6B6B` (Red)
- **Fear**: `#845EC2` (Purple)
- **Love**: `#FF9EAA` (Pink)
- **Surprise**: `#4ECDC4` (Teal)
- **Disgust**: `#4CAF50` (Green)
- **Anticipation**: `#FF9800` (Orange)

## 🔧 Component Architecture

### Common Components
- **Button**: Reusable button with variants (primary, secondary, danger, ghost)
- **Input**: Form input with label, icon, and error state
- **Loader**: Loading spinner with customizable size
- **ErrorMessage**: Error display with close button

### Layout Components
- **Header**: App header with branding and user menu
- **Footer**: App footer
- **Layout**: Wraps pages with header and footer

### Feature Components
- **EmotionBadge**: Displays detected emotion with confidence
- **EmotionScores**: Shows emotion breakdown chart
- **LyricsCard**: Displays generated lyrics with copy button
- **HistoryItem**: Expandable history item
- **HistoryList**: List of user's analysis history

## 📘 Custom Hooks

### useAnalysis
Manages text analysis workflow (emotion detection → lyrics generation)
```javascript
const { analyze, loading, result, error, reset } = useAnalysis();
```

### useHistory
Manages user's analysis history
```javascript
const { history, loading, error, fetchHistory, deleteItem } = useHistory();
```

## 🔐 Services

### apiService
Centralized API client for all backend calls
- `signup(name, email, password)`
- `login(email, password)`
- `analyze(text)`
- `getHistory()`
- `deleteHistory(id)`

### authService
Authentication management
- `signup(name, email, password)`
- `login(email, password)`
- `logout()`
- `getCurrentUser()`
- `isAuthenticated()`

### storageService
LocalStorage management
- `getToken()`, `setToken(token)`
- `getUser()`, `setUser(user)`
- `clearAuth()`

## 🚀 Features

### 1. **Authentication**
- Sign up with name, email, password
- Sign in with email and password
- JWT token-based authentication
- Persistent sessions with localStorage

### 2. **Text Analysis**
- User inputs text describing their feelings
- Model 1: Detects emotion from text
- Model 2: Generates lyrics based on emotion
- Shows emotion confidence and breakdown

### 3. **History Management**
- Saves all analyses to user history
- View past analyses with full details
- Delete individual history items
- Expandable history cards

### 4. **User Experience**
- Responsive design for all screen sizes
- Loading states and error handling
- Smooth animations and transitions
- Example prompts for quick start
- Copy lyrics to clipboard

## 🔄 Data Flow

```
User Input (Text)
      ↓
  API Service
      ↓
Backend Model 1 (Emotion Detection)
      ↓
Backend Model 2 (Lyrics Generation)
      ↓
  Display Results
      ↓
  Save to History
```

## 🎯 Key Features

1. **Modular Architecture**: Components, hooks, services separated
2. **Type Safety**: PropTypes for components (can be upgraded to TypeScript)
3. **Error Handling**: Comprehensive error handling at all levels
4. **Loading States**: Clear loading indicators
5. **Responsive Design**: Works on all devices
6. **Accessibility**: Semantic HTML and ARIA labels
7. **Performance**: React hooks for optimal rendering
8. **Maintainability**: Clear folder structure and naming conventions

## 📦 Dependencies

```json
{
  "react": "^18.x",
  "react-dom": "^18.x",
  "vite": "^5.x"
}
```

## 🌐 Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## 🚀 Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

4. Preview production build:
   ```bash
   npm run preview
   ```

## 🔮 Future Enhancements

- [ ] TypeScript migration
- [ ] Unit tests with Vitest
- [ ] E2E tests with Playwright
- [ ] Dark/Light theme toggle
- [ ] Export lyrics as PDF
- [ ] Share lyrics on social media
- [ ] Save favorite lyrics
- [ ] User profile settings
- [ ] Password reset functionality
- [ ] Email verification
