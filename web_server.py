"""
Flask Web Server for Job Application Bot
Provides web interface to control and monitor the bot
"""

import os
import json
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from job_application_bot import JobApplicationBot

app = Flask(__name__)
CORS(app)

# Global bot instance and status
bot_instance = None
bot_status = {
    "running": False,
    "current_step": "",
    "progress": 0,
    "message": "Ready to start",
    "results": None,
    "error": None
}

# Custom logging handler to capture bot logs
class WebLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
    
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage()
        }
        self.logs.append(log_entry)
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs.pop(0)

web_log_handler = WebLogHandler()
web_log_handler.setLevel(logging.INFO)


def run_bot_thread():
    """Run bot in a separate thread"""
    global bot_instance, bot_status
    
    try:
        bot_status["running"] = True
        bot_status["error"] = None
        bot_status["current_step"] = "Initializing..."
        bot_status["progress"] = 5
        bot_status["message"] = "Starting job application bot..."
        
        # Initialize bot
        bot_instance = JobApplicationBot("config.json")
        
        # Add web log handler
        logger = logging.getLogger()
        logger.addHandler(web_log_handler)
        
        # Step 1: Login
        bot_status["current_step"] = "Logging in to platforms..."
        bot_status["progress"] = 15
        bot_status["message"] = "Authenticating with job platforms..."
        login_results = bot_instance.login_all_platforms()
        
        if not any(login_results.values()):
            bot_status["error"] = "Failed to login to any platform"
            bot_status["running"] = False
            return
        
        # Step 2: Search jobs
        bot_status["current_step"] = "Searching for jobs..."
        bot_status["progress"] = 30
        bot_status["message"] = "Searching jobs across all platforms..."
        bot_instance.search_all_platforms()
        
        if not bot_instance.all_jobs:
            bot_status["error"] = "No jobs found"
            bot_status["running"] = False
            return
        
        # Step 3: Match jobs
        bot_status["current_step"] = "Matching jobs with profile..."
        bot_status["progress"] = 50
        bot_status["message"] = f"Found {len(bot_instance.all_jobs)} jobs. Matching with your profile..."
        bot_instance.match_jobs()
        
        if not bot_instance.matched_jobs:
            bot_status["error"] = "No jobs matched your profile"
            bot_status["running"] = False
            return
        
        # Step 4: Apply to jobs
        bot_status["current_step"] = "Applying to jobs..."
        bot_status["progress"] = 70
        bot_status["message"] = f"Found {len(bot_instance.matched_jobs)} matching jobs. Starting applications..."
        apply_results = bot_instance.apply_to_jobs()
        
        # Step 5: Generate results
        bot_status["current_step"] = "Generating report..."
        bot_status["progress"] = 90
        bot_status["message"] = "Finalizing results..."
        
        # Save results
        bot_instance.save_results()
        
        # Prepare results summary
        bot_status["results"] = {
            "total_jobs_found": len(bot_instance.all_jobs),
            "matched_jobs_count": len(bot_instance.matched_jobs),
            "applied_jobs_count": len(bot_instance.applied_jobs),
            "failed_applications_count": len(bot_instance.failed_applications),
            "top_matched_jobs": [
                {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "score": round(job.match_score, 1),
                    "url": job.url
                }
                for job in bot_instance.matched_jobs[:20]
            ],
            "applied_jobs": bot_instance.applied_jobs[:50],
            "report": bot_instance.generate_report()
        }
        
        bot_status["current_step"] = "Complete"
        bot_status["progress"] = 100
        bot_status["message"] = f"Successfully applied to {len(bot_instance.applied_jobs)} jobs!"
        
    except Exception as e:
        bot_status["error"] = str(e)
        bot_status["message"] = f"Error: {str(e)}"
        logging.error(f"Bot error: {str(e)}", exc_info=True)
    finally:
        bot_status["running"] = False


@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current bot status"""
    return jsonify(bot_status)


@app.route('/api/start', methods=['POST'])
def start_bot():
    """Start the job application bot"""
    global bot_status
    
    if bot_status["running"]:
        return jsonify({"error": "Bot is already running"}), 400
    
    # Check if config.json exists
    if not os.path.exists("config.json"):
        return jsonify({
            "error": "config.json not found. Please create it from config.json.example"
        }), 400
    
    # Reset status
    bot_status = {
        "running": False,
        "current_step": "",
        "progress": 0,
        "message": "Starting...",
        "results": None,
        "error": None
    }
    web_log_handler.logs.clear()
    
    # Start bot in separate thread
    thread = threading.Thread(target=run_bot_thread, daemon=True)
    thread.start()
    
    return jsonify({"message": "Bot started successfully", "status": "running"})


@app.route('/api/stop', methods=['POST'])
def stop_bot():
    """Stop the bot (if possible)"""
    global bot_status, bot_instance
    
    if not bot_status["running"]:
        return jsonify({"error": "Bot is not running"}), 400
    
    # Try to close browsers
    if bot_instance:
        try:
            for bot in bot_instance.bots.values():
                bot.close()
        except:
            pass
    
    bot_status["running"] = False
    bot_status["message"] = "Stopped by user"
    
    return jsonify({"message": "Bot stopped"})


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get bot logs"""
    return jsonify({"logs": web_log_handler.logs})


@app.route('/api/results', methods=['GET'])
def get_results():
    """Get bot results"""
    if bot_status["results"]:
        return jsonify(bot_status["results"])
    return jsonify({"error": "No results available"}), 404


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration (without credentials)"""
    try:
        with open("config.json", 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Remove sensitive data
        safe_config = config.copy()
        if "credentials" in safe_config:
            safe_config["credentials"] = {
                platform: {"email": "***", "password": "***"}
                for platform in safe_config["credentials"]
            }
        
        return jsonify(safe_config)
    except FileNotFoundError:
        return jsonify({"error": "config.json not found"}), 404


if __name__ == '__main__':
    print("="*60)
    print("Job Application Bot - Web Server")
    print("="*60)
    print("\nStarting web server on http://localhost:5000")
    print("Open your browser and navigate to the URL above")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
