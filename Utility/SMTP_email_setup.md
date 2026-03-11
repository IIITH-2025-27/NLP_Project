
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SMTP Email Configuration for OTP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# For Gmail:
# 1. Enable 2-Factor Authentication on your Google Account
# 2. Generate an App Password: https://myaccount.google.com/apppasswords
# 3. Use the generated 16-character password below


# pass : umhk udhr iymw xqtj

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Setup Instructions for Gmail SMTP:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# 1. Go to your Google Account: https://myaccount.google.com/
# 2. Navigate to Security
# 3. Enable 2-Step Verification if not already enabled
# 4. Go to App passwords: https://myaccount.google.com/apppasswords
# 5. Select app: "Mail" and device: "Other (Custom name)"
# 6. Name it "LyricMind" and click Generate
# 7. Copy the 16-character password and paste it as SMTP_PASSWORD above
# 8. Use your Gmail address as SMTP_USER
#
# For other email providers:
# - Outlook/Hotmail: SMTP_HOST=smtp-mail.outlook.com, SMTP_PORT=587
# - Yahoo: SMTP_HOST=smtp.mail.yahoo.com, SMTP_PORT=587
# - Custom SMTP: Update SMTP_HOST and SMTP_PORT accordingly
#
