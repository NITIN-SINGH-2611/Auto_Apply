# Quick Start Guide 🚀

Get your job application bot running in 5 minutes!

## Step 1: Install Dependencies

```bash
cd Agent
pip install -r requirements.txt
```

## Step 2: Setup Configuration

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

## Step 3: Run the Bot

```bash
python run_bot.py
```

Or directly:
```bash
python job_application_bot.py
```

## Step 4: Review Results

After execution, check:
- `job_bot_report.txt` - Human-readable summary
- `job_search_results.json` - Detailed JSON results
- `job_bot.log` - Execution logs

## First Time Setup Tips

1. **Test with Auto-Apply OFF**: Set `"auto_apply": false` in config.json first to see what jobs match
2. **Start with One Platform**: Comment out other platforms in credentials to test one at a time
3. **Check Logs**: Monitor `job_bot.log` for any issues

## Troubleshooting

### ChromeDriver Issues
If you get ChromeDriver errors, install it:
```bash
pip install webdriver-manager
```

### Login Fails
- Check your credentials are correct
- Some platforms may require 2FA - complete it manually if prompted
- LinkedIn may require security verification on first login

### No Jobs Found
- Try different keywords
- Check if locations are correct
- Verify you're logged in successfully

## Next Steps

- Customize keywords in `config.json` to match your target roles
- Adjust `min_match_score` to be more/less selective
- Update your profile skills to improve matching
- Review matched jobs before enabling auto-apply

---

**Ready to find your dream job! 🎯**
