# 🎵 LyricMind — Emotion-Driven Lyric Generator

An intelligent NLP application that analyzes emotions from text or images and generates creative lyrics based on the detected emotions.

**Features:**
- 📝 Text emotion analysis
- 🖼️ Image emotion detection
- 🎵 AI-powered lyric generation
- 📊 Real-time emotion scoring
- 📜 History tracking with search

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

| Software | Version | Check Command |
|----------|---------|---------------|
| Python | 3.8+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 8+ | `npm --version` |

> **Note:** MongoDB Atlas (cloud database) is used for this project. No local MongoDB installation required.

### Install/Upgrade Node.js (if needed)

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version  # Verify v18.x.x
```

**macOS:**
```bash
brew install node@18
node --version  # Verify v18.x.x
```

---

## 🚀 Installation

### Step 1: Clone Repository (if not already done)
```bash
git clone <repository-url>
cd NLP_Project/Web
```

### Step 2: Setup MongoDB Atlas (Cloud Database)

1. Create free account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (M0 free tier)
3. Create database user:
   - Navigate to **Database Access** → **Add New Database User**
   - Choose **Password** authentication
   - Save the username and password (you'll need these)
4. Whitelist your IP:
   - Navigate to **Network Access** → **Add IP Address**
   - Add `0.0.0.0/0` (allow from anywhere) or your specific IP
5. Get connection string:
   - Click **Connect** on your cluster → **Connect your application**
   - Copy the connection string: `mongodb+srv://<username>:<password>@cluster.xxxxx.mongodb.net/`

### Step 3: Setup Python Virtual Environment
```bash
# From NLP_Project directory (parent of Web)
cd ..
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 4: Install Backend Dependencies
```bash
cd Web/backend
pip install -r requirements.txt
```

### Step 5: Configure Backend Environment
Create a `.env` file in the `backend/` directory:

```bash
# From Web/backend directory
touch .env
```

Add the following content to `.env`:

```env
MONGO_URL=mongodb+srv://your-username:your-password@cluster.xxxxx.mongodb.net/lyricmind?retryWrites=true&w=majority
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
```

> **⚠️ Important:** Replace `your-username`, `your-password`, `cluster.xxxxx.mongodb.net`, and `SECRET_KEY` with your actual MongoDB Atlas credentials.

### Step 6: Install Frontend Dependencies
```bash
cd ../frontend  # From backend, go to frontend
npm install
npm install vite dotenv
```

> **Note:** Vite and dotenv may need to be installed separately if not included in package.json

### Step 7: Configure Frontend Environment (Optional)
Create a `.env` file in the `frontend/` directory if you need to change the API URL:

```bash
# From Web/frontend directory
touch .env
```

Add (only if backend is NOT on localhost:8000):
```env
VITE_API_URL=http://localhost:8000
```

---

## ▶️ How to Run

### Quick Start (2 Terminal Windows Required)

#### Terminal 1: Backend Server
```bash
# Navigate to project root and activate virtual environment
cd NLP_Project
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Navigate to backend and start server
cd Web/backend
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

✅ Backend is now running at **http://localhost:8000**

#### Terminal 2: Frontend Development Server
```bash
# Navigate to frontend
cd NLP_Project/Web/frontend

# Start development server
npm run dev
```

**Expected output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ Frontend is now running at **http://localhost:5173**

### Access the Application

1. Open your browser and navigate to **http://localhost:5173**
2. **Sign up** for a new account
3. **Login** with your credentials
4. Start using the application:
   - Enter text or upload an image
   - View emotion analysis and generated lyrics
   - Browse your analysis history

---

## 🛠️ Troubleshooting

### Backend Issues

**Issue:** `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Issue:** `pymongo.errors.ServerSelectionTimeoutError`
- Verify MONGO_URL in `.env` file is correct
- Check MongoDB Atlas IP whitelist includes your current IP
- Verify database username and password are correct
- Ensure your MongoDB Atlas cluster is active (not paused)

**Issue:** `uvicorn: command not found`
```bash
# Activate virtual environment first
source .venv/bin/activate
# Then run uvicorn from backend directory
cd Web/backend
uvicorn main:app --reload
```

### Frontend Issues

**Issue:** `Error: Cannot find module 'vite'`
```bash
cd Web/frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue:** `Port 5173 already in use`
```bash
# Kill the process using port 5173
lsof -ti:5173 | xargs kill -9
# Or use a different port
npm run dev -- --port 5174
```

---

## 📁 Project Structure

```
Web/
├── backend/
│   ├── main.py          # FastAPI routes
│   ├── ml_service.py    # ML models (emotion detection, lyrics generation)
│   ├── database.py      # MongoDB connection
│   ├── models.py        # Pydantic models
│   ├── auth.py          # Authentication logic
│   ├── requirements.txt # Python dependencies
│   └── .env            # Environment variables (create this)
│
└── frontend/
    ├── src/
    │   ├── pages/       # React pages (Dashboard, Auth)
    │   ├── components/  # Reusable components
    │   ├── services/    # API services
    │   └── assets/      # Styles and static files
    ├── package.json     # Node.js dependencies
    └── .env            # Environment variables (optional)
```

---

## 🔑 Environment Variables Reference

### Backend (.env)
| Variable | Description | Example |
|----------|-------------|---------|
| `MONGO_URL` | MongoDB Atlas connection string | `mongodb+srv://user:pass@cluster.mongodb.net/lyricmind` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | `your-secret-key-min-32-characters` |

### Frontend (.env) - Optional
| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:8000` |

---

## 👥 Support

For issues or questions, please refer to the main project documentation or create an issue in the repository
