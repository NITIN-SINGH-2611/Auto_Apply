"""
Main Job Application Bot
Orchestrates job search and application across multiple platforms
"""

import json
import logging
import time
from typing import List, Dict
from datetime import datetime
from profile_matcher import ProfileMatcher, JobMatch
from naukri_bot import NaukriBot
from linkedin_bot import LinkedInBot
from indeed_bot import IndeedBot


class JobApplicationBot:
    """Main bot that coordinates job search and applications"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize the bot with configuration"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Initialize profile matcher
        self.profile_matcher = ProfileMatcher(self.config.get("profile", {}))
        
        # Initialize platform bots
        self.bots = {}
        self._initialize_bots()
        
        # Track results
        self.all_jobs = []
        self.matched_jobs = []
        self.applied_jobs = []
        self.failed_applications = []
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}. Please create config.json from config.json.example")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {str(e)}")
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = self.config.get("settings", {}).get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('job_bot.log'),
                logging.StreamHandler()
            ]
        )
    
    def _initialize_bots(self):
        """Initialize bots for each platform"""
        credentials = self.config.get("credentials", {})
        
        if "naukri" in credentials and credentials["naukri"].get("email"):
            self.bots["naukri"] = NaukriBot(
                credentials["naukri"],
                self.profile_matcher,
                self.config
            )
        
        if "linkedin" in credentials and credentials["linkedin"].get("email"):
            self.bots["linkedin"] = LinkedInBot(
                credentials["linkedin"],
                self.profile_matcher,
                self.config
            )
        
        if "indeed" in credentials and credentials["indeed"].get("email"):
            self.bots["indeed"] = IndeedBot(
                credentials["indeed"],
                self.profile_matcher,
                self.config
            )
    
    def login_all_platforms(self) -> Dict[str, bool]:
        """Login to all configured platforms"""
        results = {}
        self.logger.info("Logging in to all platforms...")
        
        for platform, bot in self.bots.items():
            try:
                self.logger.info(f"Initializing {platform} bot...")
                bot.initialize_driver()
                time.sleep(2)
                
                self.logger.info(f"Logging in to {platform}...")
                success = bot.login()
                results[platform] = success
                
                if success:
                    self.logger.info(f"✓ Successfully logged in to {platform}")
                else:
                    self.logger.error(f"✗ Failed to login to {platform}")
                    
            except Exception as e:
                self.logger.error(f"Error logging in to {platform}: {str(e)}")
                results[platform] = False
        
        return results
    
    def search_all_platforms(self) -> List[Dict]:
        """Search for jobs across all platforms"""
        self.logger.info("Starting job search across all platforms...")
        all_jobs = []
        
        keywords = self.config.get("job_search", {}).get("keywords", [])
        locations = self.config.get("job_search", {}).get("locations", [])
        
        for platform, bot in self.bots.items():
            try:
                self.logger.info(f"Searching jobs on {platform}...")
                
                # Search with each location
                for location in locations[:3]:  # Limit to first 3 locations
                    jobs = bot.search_jobs(keywords, location)
                    all_jobs.extend(jobs)
                    time.sleep(2)  # Delay between searches
                
                # Also search without location
                jobs = bot.search_jobs(keywords, "")
                all_jobs.extend(jobs)
                
            except Exception as e:
                self.logger.error(f"Error searching {platform}: {str(e)}")
                continue
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.get("url") and job["url"] not in seen_urls:
                seen_urls.add(job["url"])
                unique_jobs.append(job)
        
        self.all_jobs = unique_jobs
        self.logger.info(f"Found {len(self.all_jobs)} unique jobs across all platforms")
        return self.all_jobs
    
    def match_jobs(self) -> List[JobMatch]:
        """Match jobs against profile and filter by score"""
        self.logger.info("Matching jobs against profile...")
        matched_jobs = []
        
        min_score = self.config.get("job_search", {}).get("min_match_score", 70)
        
        for job in self.all_jobs:
            try:
                score, details = self.profile_matcher.calculate_match_score(
                    job.get("title", ""),
                    job.get("description", ""),
                    job.get("requirements", ""),
                    job.get("experience", "")
                )
                
                if self.profile_matcher.is_job_eligible(score, min_score):
                    job_match = JobMatch(
                        title=job.get("title", ""),
                        company=job.get("company", ""),
                        location=job.get("location", ""),
                        description=job.get("description", ""),
                        url=job.get("url", ""),
                        match_score=score,
                        matched_skills=details.get("matched_skills", []),
                        missing_skills=details.get("missing_skills", []),
                        experience_match=details.get("experience_match", True),
                        reason=details.get("reason", "")
                    )
                    matched_jobs.append(job_match)
                    
            except Exception as e:
                self.logger.warning(f"Error matching job {job.get('title', '')}: {str(e)}")
                continue
        
        # Sort by match score (highest first)
        matched_jobs.sort(key=lambda x: x.match_score, reverse=True)
        
        self.matched_jobs = matched_jobs
        self.logger.info(f"Found {len(self.matched_jobs)} jobs matching profile (score >= {min_score})")
        return self.matched_jobs
    
    def apply_to_jobs(self, max_applications: int = None) -> Dict:
        """Apply to matched jobs"""
        if not self.matched_jobs:
            self.logger.warning("No matched jobs to apply to")
            return {"applied": 0, "failed": 0}
        
        auto_apply = self.config.get("job_search", {}).get("auto_apply", True)
        if not auto_apply:
            self.logger.info("Auto-apply is disabled. Showing matched jobs only.")
            return {"applied": 0, "failed": 0}
        
        apply_delay = self.config.get("job_search", {}).get("apply_delay_seconds", 5)
        max_apps = max_applications or len(self.matched_jobs)
        
        self.logger.info(f"Starting to apply to {min(max_apps, len(self.matched_jobs))} jobs...")
        
        applied_count = 0
        failed_count = 0
        
        for i, job_match in enumerate(self.matched_jobs[:max_apps]):
            try:
                self.logger.info(f"\n[{i+1}/{max_apps}] Applying to: {job_match.title} at {job_match.company}")
                self.logger.info(f"Match Score: {job_match.match_score:.1f}% - {job_match.reason}")
                
                # Determine which bot to use based on platform
                platform = self._get_platform_from_url(job_match.url)
                bot = self.bots.get(platform)
                
                if not bot:
                    self.logger.warning(f"No bot available for platform: {platform}")
                    failed_count += 1
                    self.failed_applications.append({
                        "job": job_match.title,
                        "reason": f"No bot for platform: {platform}"
                    })
                    continue
                
                # Apply to job
                success = bot.apply_to_job(job_match.url)
                
                if success:
                    applied_count += 1
                    self.applied_jobs.append({
                        "title": job_match.title,
                        "company": job_match.company,
                        "url": job_match.url,
                        "score": job_match.match_score,
                        "platform": platform
                    })
                    self.logger.info(f"✓ Successfully applied to {job_match.title}")
                else:
                    failed_count += 1
                    self.failed_applications.append({
                        "job": job_match.title,
                        "url": job_match.url,
                        "reason": "Application failed"
                    })
                    self.logger.warning(f"✗ Failed to apply to {job_match.title}")
                
                # Delay between applications
                if i < max_apps - 1:
                    time.sleep(apply_delay)
                    
            except Exception as e:
                self.logger.error(f"Error applying to {job_match.title}: {str(e)}")
                failed_count += 1
                continue
        
        self.logger.info(f"\n=== Application Summary ===")
        self.logger.info(f"Applied: {applied_count}")
        self.logger.info(f"Failed: {failed_count}")
        
        return {"applied": applied_count, "failed": failed_count}
    
    def _get_platform_from_url(self, url: str) -> str:
        """Determine platform from job URL"""
        url_lower = url.lower()
        if "naukri.com" in url_lower:
            return "naukri"
        elif "linkedin.com" in url_lower:
            return "linkedin"
        elif "indeed.com" in url_lower:
            return "indeed"
        return "unknown"
    
    def generate_report(self) -> str:
        """Generate a summary report"""
        report = f"""
{'='*60}
JOB APPLICATION BOT - EXECUTION REPORT
{'='*60}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY:
--------
Total Jobs Found: {len(self.all_jobs)}
Matched Jobs (Score >= 70): {len(self.matched_jobs)}
Successfully Applied: {len(self.applied_jobs)}
Failed Applications: {len(self.failed_applications)}

TOP MATCHED JOBS:
-----------------
"""
        for i, job in enumerate(self.matched_jobs[:20], 1):
            report += f"\n{i}. {job.title} at {job.company}\n"
            report += f"   Location: {job.location}\n"
            report += f"   Match Score: {job.match_score:.1f}%\n"
            report += f"   Matched Skills: {', '.join(job.matched_skills[:5])}\n"
            report += f"   URL: {job.url}\n"
        
        if self.applied_jobs:
            report += f"\n\nSUCCESSFULLY APPLIED JOBS:\n"
            report += "-" * 60 + "\n"
            for job in self.applied_jobs:
                report += f"✓ {job['title']} at {job['company']} ({job['platform']})\n"
        
        return report
    
    def save_results(self, filename: str = "job_search_results.json"):
        """Save results to JSON file"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_jobs_found": len(self.all_jobs),
            "matched_jobs_count": len(self.matched_jobs),
            "applied_jobs_count": len(self.applied_jobs),
            "matched_jobs": [
                {
                    "title": job.title,
                    "company": job.company,
                    "location": job.location,
                    "url": job.url,
                    "match_score": job.match_score,
                    "matched_skills": job.matched_skills,
                    "reason": job.reason
                }
                for job in self.matched_jobs
            ],
            "applied_jobs": self.applied_jobs,
            "failed_applications": self.failed_applications
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filename}")
    
    def run(self):
        """Run the complete job search and application process"""
        try:
            self.logger.info("="*60)
            self.logger.info("STARTING JOB APPLICATION BOT")
            self.logger.info("="*60)
            
            # Step 1: Login
            login_results = self.login_all_platforms()
            if not any(login_results.values()):
                self.logger.error("Failed to login to any platform. Exiting.")
                return
            
            # Step 2: Search jobs
            self.search_all_platforms()
            
            if not self.all_jobs:
                self.logger.warning("No jobs found. Exiting.")
                return
            
            # Step 3: Match jobs
            self.match_jobs()
            
            if not self.matched_jobs:
                self.logger.warning("No jobs matched your profile. Exiting.")
                return
            
            # Ensure we have at least 50 matches (or as many as available)
            target_count = 50
            if len(self.matched_jobs) < target_count:
                self.logger.info(f"Found {len(self.matched_jobs)} matching jobs (target: {target_count})")
            else:
                self.logger.info(f"Found {len(self.matched_jobs)} matching jobs (target: {target_count}) ✓")
            
            # Step 4: Apply to jobs
            apply_results = self.apply_to_jobs()
            
            # Step 5: Generate report
            report = self.generate_report()
            print(report)
            
            # Save results
            self.save_results()
            
            # Save report to file
            with open("job_bot_report.txt", 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info("\n" + "="*60)
            self.logger.info("JOB APPLICATION BOT COMPLETED")
            self.logger.info("="*60)
            
        except Exception as e:
            self.logger.error(f"Error in bot execution: {str(e)}", exc_info=True)
        finally:
            # Close all browsers
            for bot in self.bots.values():
                try:
                    bot.close()
                except:
                    pass


if __name__ == "__main__":
    bot = JobApplicationBot("config.json")
    bot.run()
