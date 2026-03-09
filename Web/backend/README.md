# Backend Structure

A clean, modular FastAPI backend for the LyricMind NLP project.

## 📁 File Structure

```
backend/
├── main.py          # FastAPI app and API routes
├── config.py        # Configuration settings
├── database.py      # MongoDB connection and collections
├── models.py        # Pydantic request/response models
├── auth.py          # Authentication utilities (JWT, password hashing)
├── ml_service.py    # ML models (emotion detection, lyric generation)
├── requirements.txt # Python dependencies
└── .env            # Environment variables
```

## 📋 Module Descriptions

### `config.py`
- Environment configuration
- JWT settings
- Database connection strings
- CORS origins

### `database.py`
- MongoDB client initialization
- Database and collection references

### `models.py`
- Pydantic models for request validation
- `SignupRequest`, `LoginRequest`, `AnalyzeRequest`

### `auth.py`
- Password hashing and verification
- JWT token creation and validation
- `get_current_user()` dependency for protected routes

### `ml_service.py`
- Emotion detection from text
- Lyric generation based on emotion
- Contains dummy models (replace with real ML models in production)

### `main.py`
- FastAPI application setup
- CORS middleware configuration
- API endpoints:
  - `GET /` - Health check
  - `POST /auth/signup` - User registration
  - `POST /auth/login` - User authentication
  - `POST /analyze` - Analyze text and generate lyrics
  - `GET /history` - Get user's analysis history
  - `DELETE /history/{record_id}` - Delete history record

## 🚀 Running the Backend

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload --port 8000
```

## 🔧 Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
MONGO_URL=mongodb://localhost:27017

# CORS Configuration (optional)
# Default: Allow all origins (for development)
# ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### CORS Configuration

By default, the backend allows connections from **any origin** (useful for development).

To restrict origins in production, set the `ALLOWED_ORIGINS` environment variable:
- Single origin: `ALLOWED_ORIGINS=https://yourdomain.com`
- Multiple origins: `ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com`

## 📝 Notes

- All ML functions are currently using dummy implementations
- Replace `predict_emotion()` and `generate_lyrics()` in `ml_service.py` with actual ML models
- The structure is kept simple and modular for easy maintenance and testing
