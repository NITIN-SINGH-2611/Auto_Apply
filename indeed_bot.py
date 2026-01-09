"""
Indeed.com Automation Bot
Handles login, job search, and application on Indeed
"""

import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from profile_matcher import ProfileMatcher, JobMatch


class IndeedBot:
    """Automation bot for Indeed.com"""
    
    def __init__(self, credentials: Dict, profile_matcher: ProfileMatcher, config: Dict):
        self.email = credentials.get("email")
        self.password = credentials.get("password")
        self.profile_matcher = profile_matcher
        self.config = config
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://www.indeed.com"
        
    def initialize_driver(self):
        """Initialize Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.config.get("settings", {}).get("headless", False):
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(self.config.get("settings", {}).get("implicit_wait", 10))
        self.driver.set_page_load_timeout(self.config.get("settings", {}).get("page_load_timeout", 30))
        
    def login(self) -> bool:
        """Login to Indeed account"""
        try:
            self.logger.info("Navigating to Indeed login page...")
            self.driver.get(f"{self.base_url}/account/login")
            time.sleep(3)
            
            # Check if already logged in
            try:
                self.driver.find_element(By.CSS_SELECTOR, "[data-testid='user-menu'], .userMenu")
                self.logger.info("Already logged in to Indeed")
                return True
            except NoSuchElementException:
                pass
            
            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "login-email-input"))
            )
            email_input.clear()
            email_input.send_keys(self.email)
            time.sleep(1)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "login-password-input")
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # Click login button
            submit_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], #login-submit-button")
            submit_btn.click()
            time.sleep(5)
            
            # Verify login
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        "[data-testid='user-menu'], .userMenu, .gnav-UserMenu"))
                )
                self.logger.info("Successfully logged in to Indeed")
                return True
            except TimeoutException:
                self.logger.error("Login failed - could not verify user session")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during Indeed login: {str(e)}")
            if self.config.get("settings", {}).get("screenshot_on_error", True):
                self.driver.save_screenshot("indeed_login_error.png")
            return False
    
    def search_jobs(self, keywords: List[str], location: str = "") -> List[Dict]:
        """Search for jobs on Indeed"""
        jobs = []
        try:
            self.logger.info(f"Searching jobs on Indeed with keywords: {keywords}")
            
            # Navigate to jobs page
            jobs_url = f"{self.base_url}/jobs"
            self.driver.get(jobs_url)
            time.sleep(3)
            
            # Enter search keywords
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "text-input-what"))
                )
                search_box.clear()
                search_box.send_keys(keywords[0] if keywords else "Java Developer")
                time.sleep(2)
            except TimeoutException:
                self.logger.warning("Could not find search box")
                return jobs
            
            # Enter location if provided
            if location:
                try:
                    location_box = self.driver.find_element(By.ID, "text-input-where")
                    location_box.clear()
                    location_box.send_keys(location)
                    time.sleep(2)
                except:
                    pass
            
            # Click search button
            try:
                search_btn = self.driver.find_element(By.CSS_SELECTOR, 
                    "button[type='submit'], #jobsearch")
                search_btn.click()
            except:
                search_box.send_keys(Keys.RETURN)
            
            time.sleep(5)
            
            # Extract job listings
            max_pages = 5
            max_jobs = self.config.get("job_search", {}).get("max_jobs_per_platform", 50)
            
            for page in range(max_pages):
                if len(jobs) >= max_jobs:
                    break
                    
                self.logger.info(f"Scraping page {page + 1}...")
                
                # Find job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, 
                    ".job_seen_beacon, .jobCard, [data-jk], .slider_item")
                
                for card in job_cards:
                    if len(jobs) >= max_jobs:
                        break
                    
                    try:
                        job_data = self._extract_job_data(card)
                        if job_data:
                            jobs.append(job_data)
                    except Exception as e:
                        self.logger.warning(f"Error extracting job data: {str(e)}")
                        continue
                
                # Go to next page
                if page < max_pages - 1 and len(jobs) < max_jobs:
                    try:
                        next_btn = self.driver.find_element(By.CSS_SELECTOR, 
                            "a[aria-label='Next Page'], .pagination .next, [data-testid='pagination-page-next']")
                        if next_btn:
                            next_btn.click()
                            time.sleep(3)
                        else:
                            break
                    except:
                        break
            
            self.logger.info(f"Found {len(jobs)} jobs on Indeed")
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching jobs on Indeed: {str(e)}")
            return jobs
    
    def _extract_job_data(self, job_card) -> Optional[Dict]:
        """Extract job data from a job card element"""
        try:
            # Title
            title_elem = job_card.find_element(By.CSS_SELECTOR, 
                ".jobTitle a, h2.jobTitle a, a[data-jk]")
            title = title_elem.text.strip()
            job_url = title_elem.get_attribute("href") or ""
            if job_url and not job_url.startswith("http"):
                job_url = f"{self.base_url}{job_url}"
            
            # Company
            try:
                company = job_card.find_element(By.CSS_SELECTOR, 
                    ".companyName, .company, [data-testid='company-name']").text.strip()
            except:
                company = "Not specified"
            
            # Location
            try:
                location = job_card.find_element(By.CSS_SELECTOR, 
                    ".companyLocation, .location, [data-testid='job-location']").text.strip()
            except:
                location = "Not specified"
            
            # Description
            description = ""
            try:
                description = job_card.find_element(By.CSS_SELECTOR, 
                    ".job-snippet, .summary, .job-snippet-container").text.strip()
            except:
                pass
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "url": job_url,
                "platform": "Indeed"
            }
        except Exception as e:
            self.logger.warning(f"Could not extract job data: {str(e)}")
            return None
    
    def apply_to_job(self, job_url: str) -> bool:
        """Apply to a job on Indeed"""
        try:
            self.logger.info(f"Applying to job: {job_url}")
            self.driver.get(job_url)
            time.sleep(5)
            
            # Look for apply button
            apply_selectors = [
                "button[data-testid='apply-button'], #apply-button-link, .jobsearch-IndeedApplyButton",
                "a[data-testid='apply-button'], .ia-IndeedApplyButton",
                "button:contains('Apply'), a:contains('Apply')"
            ]
            
            apply_btn = None
            for selector in apply_selectors:
                try:
                    apply_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    break
                except:
                    continue
            
            if not apply_btn:
                self.logger.warning("Apply button not found")
                return False
            
            # Check if already applied
            if "applied" in apply_btn.text.lower():
                self.logger.info("Already applied to this job")
                return True
            
            apply_btn.click()
            time.sleep(3)
            
            # Handle application form
            try:
                # Fill required fields if needed
                # Indeed might redirect to external site or use their own form
                submit_btn = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 
                        "button[type='submit'], button:contains('Continue'), button:contains('Submit')"))
                )
                submit_btn.click()
                time.sleep(3)
                self.logger.info("Successfully applied to job")
                return True
            except:
                # Might be external application
                self.logger.info("Application may require external site - check manually")
                return False
            
        except Exception as e:
            self.logger.error(f"Error applying to job: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
