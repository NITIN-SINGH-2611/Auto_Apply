# Web Interface Guide 🌐

## Overview

The Job Application Bot now includes a beautiful web interface that lets you control the bot with a single click!

## Features

### 🎨 Modern Web Interface
- Beautiful gradient design
- Real-time progress tracking
- Live status updates
- Activity logs
- Results dashboard

### 🚀 One-Click Operation
- Single "Apply" button to start everything
- No command line needed
- Visual feedback throughout the process

### 📊 Real-Time Updates
- Progress bar (0-100%)
- Current step indicator
- Status messages
- Activity logs
- Results as they come in

## How It Works

### Architecture

```
Web Browser (Frontend)
    ↓
Flask Web Server (Backend)
    ↓
Job Application Bot (Core Logic)
    ↓
Platform Bots (Naukri, LinkedIn, Indeed)
```

### Components

1. **`web_server.py`**: Flask server with API endpoints
2. **`templates/index.html`**: Beautiful web interface
3. **`job_application_bot.py`**: Core bot logic
4. **Platform bots**: Naukri, LinkedIn, Indeed automation

### API Endpoints

- `GET /` - Web interface
- `GET /api/status` - Get bot status
- `POST /api/start` - Start the bot
- `POST /api/stop` - Stop the bot
- `GET /api/logs` - Get activity logs
- `GET /api/results` - Get results
- `GET /api/config` - Get configuration (safe)

## User Flow

1. **User opens browser** → `http://localhost:5000`
2. **User clicks "Apply" button** → Sends POST to `/api/start`
3. **Server starts bot** → In background thread
4. **Frontend polls status** → Every 1-2 seconds
5. **Progress updates** → Progress bar, messages, logs
6. **Results displayed** → Statistics and job list

## Status States

- **Ready**: Bot is idle, ready to start
- **Running**: Bot is actively processing
- **Complete**: Bot finished successfully
- **Error**: Bot encountered an error

## Progress Stages

1. **0-15%**: Initialization and login
2. **15-30%**: Job searching
3. **30-50%**: Job matching
4. **50-70%**: Applying to jobs
5. **70-100%**: Generating reports

## Security Features

- Credentials never exposed in API
- Config file not accessible via web
- Safe error handling
- No sensitive data in logs

## Customization

### Change Port

Edit `web_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Change Update Frequency

Edit `templates/index.html`:
```javascript
statusCheckInterval = setInterval(updateStatus, 1000);  // Change 1000ms
```

### Customize Styling

Edit `templates/index.html` - CSS is in `<style>` tag

## Troubleshooting

### Web page won't load
- Check if server is running
- Verify port 5000 is available
- Check firewall settings

### Button doesn't work
- Open browser console (F12) for errors
- Check if config.json exists
- Verify Flask is installed

### No status updates
- Check browser console for errors
- Verify API endpoints are working
- Check server logs

## Next Steps

1. Run `python web_server.py`
2. Open `http://localhost:5000`
3. Click "Start Job Application"
4. Watch the magic happen! ✨

---

**Enjoy your automated job search! 🎯**
