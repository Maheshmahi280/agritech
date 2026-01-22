# 🚀 Quick Start Guide

## Option 1: Double-Click to Start (EASIEST)
1. **Double-click** `start_server.bat` file
2. Server will start automatically
3. Open browser: http://127.0.0.1:8000/

## Option 2: Command Line
```bash
cd "d:\agritech --hackathon\myproject"
python manage.py runserver
```

## Option 3: Always Online (Deploy to Cloud)
Deploy to Railway/Render for 24/7 access:
- Railway: https://railway.app
- Render: https://render.com

## ⚠️ Important Notes
- Keep the terminal window open while using the website
- If you close the terminal, the website stops working
- For permanent hosting, use Option 3 (deployment)

## 🔧 Troubleshooting
If website doesn't open:
1. Run `start_server.bat`
2. Wait for "Starting development server" message
3. Go to http://127.0.0.1:8000/

## 📱 Access from Phone/Other Devices
```bash
python manage.py runserver 0.0.0.0:8000
```
Then use: http://YOUR_COMPUTER_IP:8000/