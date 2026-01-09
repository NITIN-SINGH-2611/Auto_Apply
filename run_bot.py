"""
Simple runner script for the Job Application Bot
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from job_application_bot import JobApplicationBot

def main():
    """Main entry point"""
    print("="*60)
    print("JOB APPLICATION BOT")
    print("="*60)
    print("\nStarting bot...\n")
    
    try:
        bot = JobApplicationBot("config.json")
        bot.run()
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease create config.json from config.json.example")
        print("and fill in your credentials and profile information.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
