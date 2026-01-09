# Quick Start - Web Interface 🚀

## 3 Simple Steps to Run

### Step 1: Install Dependencies
```bash
cd Agent
pip install -r requirements.txt
```

### Step 2: Configure
```bash
copy config.json.example config.json
```
Then edit `config.json` with your credentials.

### Step 3: Start Web Server
```bash
python web_server.py
```

Or double-click: **`start_web.bat`**

### Step 4: Open Browser
Go to: **http://localhost:5000**

### Step 5: Click "Start Job Application" Button
That's it! The bot will:
- ✅ Login to all platforms
- 🔍 Search for jobs
- 🎯 Match jobs with your profile
- 📝 Apply automatically
- 📊 Show results in real-time

---

## What You'll See

1. **Big Apply Button** - Click to start
2. **Progress Bar** - Shows 0-100% progress
3. **Status Messages** - Current step and updates
4. **Activity Logs** - Real-time bot activity
5. **Results** - Statistics and matched jobs

---

## Troubleshooting

**Port 5000 in use?** 
- Change port in `web_server.py` (line 150)

**Module not found?**
- Run: `pip install -r requirements.txt`

**Config not found?**
- Copy `config.json.example` to `config.json`

---

**That's it! Happy job hunting! 🎯**
