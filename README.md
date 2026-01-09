# Job Application Bot 🤖

An intelligent automation bot that searches for jobs across multiple platforms (Naukri, LinkedIn, Indeed) and automatically applies to positions matching your profile.

## Features

- 🔐 **Secure Login**: Automatically logs into Naukri, LinkedIn, and Indeed
- 🔍 **Smart Job Search**: Searches jobs based on your keywords and locations
- 🎯 **Profile Matching**: Intelligent matching algorithm that scores jobs based on:
  - Skills match (40 points)
  - Keyword relevance (20 points)
  - Experience requirements (20 points)
  - Role title match (10 points)
  - Education match (10 points)
- 📊 **Auto-Application**: Automatically applies to jobs matching your profile
- 📈 **Detailed Reports**: Generates comprehensive reports of all jobs found and applied
- 🎨 **Configurable**: Easy-to-use JSON configuration

## Prerequisites

1. **Python 3.8+** installed on your system
2. **Google Chrome** browser installed
3. **ChromeDriver** (will be installed automatically via webdriver-manager)

## Installation

1. **Navigate to the Agent folder:**
   ```bash
   cd Agent
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Configuration:**
   - Copy `config.json.example` to `config.json`
   - Fill in your credentials and profile information

## Configuration

Edit `config.json` with your information:

### 1. Credentials
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
  }
}
```

### 2. Profile Information
Update your profile with:
- Skills
- Experience years
- Education details
- Resume path
- Cover letter

### 3. Job Search Parameters
Configure:
- Keywords to search
- Locations
- Experience range
- Minimum match score (default: 70)
- Auto-apply setting

## Usage

### Basic Usage

```bash
python job_application_bot.py
```

### What the Bot Does

1. **Login Phase**: Logs into all configured platforms
2. **Search Phase**: Searches for jobs using your keywords and locations
3. **Matching Phase**: Scores and filters jobs based on your profile
4. **Application Phase**: Automatically applies to matching jobs
5. **Reporting Phase**: Generates detailed reports

### Output Files

- `job_bot.log` - Detailed execution log
- `job_search_results.json` - Complete results in JSON format
- `job_bot_report.txt` - Human-readable summary report

## How Profile Matching Works

The bot uses an intelligent scoring system:

- **Skills Match (40%)**: Checks how many of your skills match the job requirements
- **Keywords (20%)**: Matches job title and description with your search keywords
- **Experience (20%)**: Compares your experience with job requirements
- **Role Title (10%)**: Matches job title with your target roles
- **Education (10%)**: Checks education requirements

Only jobs with a score >= 70% (configurable) are considered for application.

## Important Notes

### ⚠️ Terms of Service

- **Use Responsibly**: This bot automates job applications. Make sure you're comfortable with this approach.
- **Rate Limiting**: The bot includes delays between applications to avoid being flagged.
- **Manual Verification**: Some applications may require manual steps (e.g., security checks, external sites).

### 🔒 Security

- **Never commit `config.json`** with real credentials to version control
- Keep your credentials secure
- Consider using environment variables for production use

### 🎯 Best Practices

1. **Review Matched Jobs**: Check `job_search_results.json` before enabling auto-apply
2. **Start Small**: Test with `auto_apply: false` first
3. **Customize Keywords**: Update keywords to match your target roles
4. **Update Profile**: Keep your profile information current

## Troubleshooting

### Login Issues

- **2FA/Verification**: If a platform requires 2FA, you may need to complete it manually
- **Wrong Credentials**: Double-check your email and password
- **Account Locked**: Some platforms may temporarily lock accounts after multiple login attempts

### Job Search Issues

- **No Jobs Found**: Try different keywords or locations
- **Slow Performance**: Increase delays in config or reduce max_jobs_per_platform

### Application Issues

- **External Sites**: Some jobs redirect to external application sites (not automated)
- **Complex Forms**: Jobs with multi-step forms may require manual completion
- **Already Applied**: The bot skips jobs you've already applied to

## Customization

### Adding New Platforms

To add support for a new platform:

1. Create a new bot class (e.g., `monster_bot.py`)
2. Implement `login()`, `search_jobs()`, and `apply_to_job()` methods
3. Add it to `job_application_bot.py` in `_initialize_bots()`

### Adjusting Match Score

Edit `min_match_score` in `config.json`:
- Higher (80-90): More selective, only best matches
- Lower (60-70): More applications, less selective

## Example Output

```
============================================================
JOB APPLICATION BOT - EXECUTION REPORT
============================================================
Date: 2024-01-15 10:30:00

SUMMARY:
--------
Total Jobs Found: 150
Matched Jobs (Score >= 70): 52
Successfully Applied: 45
Failed Applications: 7

TOP MATCHED JOBS:
-----------------
1. Java Backend Developer at Tech Corp
   Location: Mumbai
   Match Score: 92.5%
   Matched Skills: Java, Spring Boot, REST APIs, Microservices
   URL: https://...
```

## Support

For issues or questions:
1. Check the logs in `job_bot.log`
2. Review the configuration in `config.json`
3. Ensure all dependencies are installed

## License

This project is for personal use. Use responsibly and in accordance with each platform's Terms of Service.

---

**Happy Job Hunting! 🚀**
