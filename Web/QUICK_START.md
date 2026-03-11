# 🚀 Quick Start Guide - OTP Authentication

## ⚡ 5-Minute Setup

### 1. Install Backend Dependencies (30 seconds)

```bash
cd Web/backend
pip install -r requirements.txt
```

### 2. Configure Gmail SMTP (3 minutes)

**A. Enable 2-Factor Authentication:**
- Visit: https://myaccount.google.com/security
- Enable "2-Step Verification"

**B. Generate App Password:**
- Visit: https://myaccount.google.com/apppasswords
- App: "Mail", Device: "Other (LyricMind)"
- Copy the 16-character password

**C. Update `.env` file:**
```bash
cd Web/backend
nano .env  # or use any editor
```

Add these lines (replace with your actual email and app password):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx
SMTP_FROM_EMAIL=your-email@gmail.com
SMTP_FROM_NAME=LyricMind
```

### 3. Start Servers (1 minute)

**Terminal 1 - Backend:**
```bash
cd Web/backend
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd Web/frontend
npm run dev
```

### 4. Test Signup (30 seconds)

1. Open http://localhost:5173
2. Click "Sign Up"
3. Enter your details
4. Click "Send OTP"
5. Check your email for the 6-digit code
6. Enter the code
7. Done! ✅

---

## 🧪 Quick Test (No UI)

Test the backend directly:

**Step 1: Request OTP**
```bash
curl -X POST http://localhost:8000/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "your-email@gmail.com",
    "password": "test123456"
  }'
```

**Expected:** Email sent to your inbox

**Step 2: Check Email**
- Open your email
- Find the 6-digit code (e.g., 123456)

**Step 3: Verify OTP**
```bash
curl -X POST http://localhost:8000/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@gmail.com",
    "otp": "123456"
  }'
```

**Expected:** Returns user info and JWT token

---

## 🐛 Quick Troubleshooting

### Email Not Sending?

**Check 1:** SMTP credentials
```bash
cd Web/backend
cat .env | grep SMTP
```
→ Should show your email and app password

**Check 2:** 2FA and App Password
- Must use **app password**, not regular password
- 2FA must be enabled on Google account

**Check 3:** Backend logs
```bash
# In backend terminal, look for errors like:
# "Failed to send email: ..."
```

### Email Not Received?

1. **Check spam folder** - Most common issue!
2. **Wait 1-2 minutes** - Email might be delayed
3. **Click "Resend OTP"** - Try again
4. **Check email address** - Make sure it's correct

### "Invalid OTP" Error?

- ✅ Check if OTP expired (10 minutes)
- ✅ Make sure you copied all 6 digits
- ✅ Maximum 5 attempts - request new OTP if exceeded

---

## 📋 Pre-Flight Checklist

Before testing, ensure:

- [ ] Python dependencies installed (`pip install -r requirements.txt`)
- [ ] Node dependencies installed (`npm install` in frontend)
- [ ] MongoDB running (check MONGO_URL in .env)
- [ ] SMTP_USER and SMTP_PASSWORD set in .env
- [ ] 2FA enabled on Gmail
- [ ] App password generated and copied to .env
- [ ] Backend starts without errors
- [ ] Frontend starts without errors

---

## 📧 Email Preview

You'll receive an email like this:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
From: LyricMind <your-email@gmail.com>
Subject: Verify Your Email - LyricMind
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎵 LyricMind

Hello Test User,

Welcome to LyricMind! 🎵

Your verification code is:

  ╔═══════════╗
  ║  1 2 3 4 5 6  ║
  ╚═══════════╝

⏱️ This code will expire in 10 minutes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🎯 Success Indicators

### Backend Running Correctly:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Frontend Running Correctly:
```
VITE v... ready in ... ms

➜  Local:   http://localhost:5173/
```

### OTP Sent Successfully:
```json
{
  "message": "OTP sent successfully to your email",
  "email": "your-email@gmail.com"
}
```

### Signup Successful:
```json
{
  "message": "Signup successful",
  "token": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "id": "...",
    "name": "Test User",
    "email": "your-email@gmail.com"
  }
}
```

---

## 🔗 Important Links

- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Google 2FA Setup:** https://myaccount.google.com/security
- **API Docs:** http://localhost:8000/docs (when backend is running)

---

## 💡 Pro Tips

1. **Use a real email you have access to** - You need to receive and read the OTP
2. **Check spam folder first** - Gmail might filter the OTP email
3. **Keep terminal windows visible** - Watch for any error messages
4. **Use different emails for testing** - Each signup needs a unique email
5. **OTP is case-sensitive** - Copy it exactly (though it's all digits)
6. **10-minute expiry** - Don't wait too long to enter the OTP

---

## 🎓 Understanding OTP Codes

- **Length:** 6 digits (e.g., 123456)
- **Character Set:** Numbers only (0-9)
- **Generation:** Cryptographically secure random
- **Validity:** 10 minutes from generation
- **Max Attempts:** 5 tries per OTP
- **One-Time Use:** Deleted after successful verification
- **Security:** Cannot be reused or bruteforced

---

## 📱 Testing on Mobile

The frontend is responsive! Test on mobile:

1. Find your local IP:
   ```bash
   ipconfig getifaddr en0  # Mac
   hostname -I  # Linux
   ipconfig  # Windows
   ```

2. Update vite config to allow network access (if needed)

3. Access from mobile: `http://YOUR-IP:5173`

---

## 🎬 Next Steps

After successful setup:

1. ✅ Test full signup flow
2. ✅ Test resend OTP functionality
3. ✅ Test error scenarios (wrong OTP, expired OTP)
4. ✅ Test login with newly created account
5. ✅ Customize email template (optional)
6. ✅ Set up production email service (SendGrid/Mailgun)

---

## 📞 Need Help?

- **SMTP Issues:** See `SMTP_SETUP.md`
- **General Setup:** See `README.md`
- **Full Details:** See `IMPLEMENTATION_SUMMARY.md`
- **Backend Errors:** Check terminal output
- **Frontend Errors:** Check browser console (F12)

---

**Time to first OTP:** ~5 minutes ⚡

**Ready? Let's go!** 🚀
