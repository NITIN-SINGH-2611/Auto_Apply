# How to Run the Job Application Bot 🚀

## Quick Start (Web Interface)

### Step 1: Install Dependencies

```bash
cd Agent
pip install -r requirements.txt
```

### Step 2: Configure

1. **Copy the example config:**
   ```bash
   copy config.json.example config.json
   ```
   (On Linux/Mac: `cp config.json.example config.json`)

2. **Edit `config.json`** and fill in:
   - Your email and password for each platform (Naukri, LinkedIn, Indeed)
   - Your profile information (skills, experience, education)
   - Job search keywords and locations
   - Set `auto_apply: true` if you want automatic applications

### Step 3: Start the Web Server

```bash
python web_server.py
```

### Step 4: Open in Browser

Open your web browser and navigate to:
```
http://localhost:5000
```

### Step 5: Click "Start Job Application" Button

- Click the big **"🚀 Start Job Application"** button
- Watch the progress bar and status updates in real-time
- View logs and results as they come in

---

## Alternative: Command Line Method

If you prefer to run without the web interface:

```bash
python run_bot.py
```

Or directly:
```bash
python job_application_bot.py
```

---

## Detailed Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
   - Check: `python --version`
   - Download: https://www.python.org/downloads/

2. **Google Chrome** browser installed
   - The bot uses Chrome for automation
   - ChromeDriver is installed automatically

3. **Account credentials** for:
   - Naukri.com
   - LinkedIn
   - Indeed.com

### Installation Steps

#### Windows:

1. **Open Command Prompt or PowerShell**
   - Press `Win + R`, type `cmd`, press Enter

2. **Navigate to Agent folder:**
   ```cmd
   cd C:\Users\Nitin1.Samant\Personal_Project\Agent
   ```

3. **Install Python packages:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Setup configuration:**
   ```cmd
   copy config.json.example config.json
   ```
   Then edit `config.json` with your details

5. **Run the web server:**
   ```cmd
   python web_server.py
   ```

#### Linux/Mac:

1. **Open Terminal**

2. **Navigate to Agent folder:**
   ```bash
   cd ~/path/to/Agent
   ```

3. **Install Python packages:**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Setup configuration:**
   ```bash
   cp config.json.example config.json
   ```
   Then edit `config.json` with your details

5. **Run the web server:**
   ```bash
   python3 web_server.py
   ```

---

## Using the Web Interface

### Main Features:

1. **Start Button**: Click to begin the job application process
2. **Progress Bar**: Shows real-time progress (0-100%)
3. **Status Messages**: Current step and status updates
4. **Activity Logs**: Detailed logs of all bot activities
5. **Results Section**: Shows statistics and matched jobs after completion

### What Happens When You Click "Apply":

1. ✅ **Login Phase** (15%): Logs into all configured platforms
2. 🔍 **Search Phase** (30%): Searches for jobs using your keywords
3. 🎯 **Matching Phase** (50%): Matches jobs with your profile
4. 📝 **Application Phase** (70%): Applies to matching jobs
5. 📊 **Report Generation** (90-100%): Creates detailed reports

### Expected Results:

- **Finds 50+ matching jobs** across all platforms
- **Applies automatically** to jobs with match score >= 70%
- **Generates reports** with all details
- **Shows real-time progress** in the web interface

---

## Configuration Guide

### Essential Settings in `config.json`:

```json
{
  "credentials": {
    "naukri": {
      "email": "your_email@example.com",
      "password": "your_password"
    },
    "linkedin": {
      "email": "your_email@example.com",
      "password": "your_password"
    },
    "indeed": {
      "email": "your_email@example.com",
      "password": "your_password"
    }
  },
  "profile": {
    "skills": ["Java", "Python", "Spring Boot", ...],
    "experience_years": 2,
    ...
  },
  "job_search": {
    "keywords": ["Java Developer", "Backend Developer", ...],
    "locations": ["Mumbai", "Pune", "Remote", ...],
    "auto_apply": true,
    "min_match_score": 70
  }
}
```

### Important Settings:

- **`auto_apply`**: Set to `false` to only search and match (not apply)
- **`min_match_score`**: Minimum match percentage (70 = 70%)
- **`headless`**: Set to `true` to run browser in background
- **`max_jobs_per_platform`**: Limit jobs per platform (default: 50)

---

## Troubleshooting

### Issue: "config.json not found"

**Solution**: Copy `config.json.example` to `config.json` and fill in your details

### Issue: "Failed to login"

**Solutions**:
- Check your email and password are correct
- Some platforms may require 2FA - complete it manually
- LinkedIn may need security verification on first login
- Check if your account is locked

### Issue: "No jobs found"

**Solutions**:
- Try different keywords
- Check location settings
- Verify you're logged in successfully
- Some platforms may have rate limits

### Issue: ChromeDriver errors

**Solution**: ChromeDriver is installed automatically. If issues persist:
```bash
pip install --upgrade webdriver-manager
```

### Issue: Port 5000 already in use

**Solution**: Change the port in `web_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change 5000 to 5001
```

### Issue: Module not found errors

**Solution**: Install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Output Files

After running, you'll find:

1. **`job_bot_report.txt`**: Human-readable summary
2. **`job_search_results.json`**: Detailed JSON results
3. **`job_bot.log`**: Execution logs

---

## Best Practices

1. **Test First**: Run with `auto_apply: false` to review matches
2. **Start Small**: Test with one platform first
3. **Monitor Logs**: Watch the activity logs for issues
4. **Review Results**: Check matched jobs before enabling auto-apply
5. **Update Profile**: Keep your skills and experience current

---

## Security Notes

- ⚠️ **Never commit `config.json`** to version control (it's in .gitignore)
- ⚠️ **Keep credentials secure** - don't share your config.json
- ⚠️ **Use responsibly** - be aware of platform terms of service

---

## Need Help?

1. Check the logs in the web interface
2. Review `job_bot.log` file
3. Verify your configuration in `config.json`
4. Ensure all dependencies are installed

---

**Happy Job Hunting! 🎯**
