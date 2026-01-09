"""
Profile Matcher - Matches job descriptions with user profile
Calculates match scores based on skills, experience, and requirements
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class JobMatch:
    """Represents a matched job with score"""
    title: str
    company: str
    location: str
    description: str
    url: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_match: bool
    reason: str


class ProfileMatcher:
    """Matches jobs against user profile"""
    
    def __init__(self, profile_config: Dict):
        self.profile = profile_config
        self.skills = [skill.lower() for skill in profile_config.get("skills", [])]
        self.experience_years = profile_config.get("experience_years", 0)
        self.keywords = [kw.lower() for kw in profile_config.get("job_search", {}).get("keywords", [])]
        
    def calculate_match_score(self, job_title: str, job_description: str, 
                            job_requirements: str = "", experience_required: str = "") -> Tuple[float, Dict]:
        """
        Calculate match score for a job posting
        Returns: (score, match_details)
        """
        score = 0.0
        max_score = 100.0
        match_details = {
            "matched_skills": [],
            "missing_skills": [],
            "experience_match": True,
            "keyword_matches": 0
        }
        
        # Combine all text for analysis
        full_text = f"{job_title} {job_description} {job_requirements}".lower()
        
        # 1. Skill Matching (40 points)
        skill_score = 0
        matched_skills = []
        missing_skills = []
        
        # Check for each skill in profile
        for skill in self.skills:
            if skill in full_text:
                skill_score += 40 / len(self.skills)
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        # Also check for variations and related terms
        skill_synonyms = {
            "java": ["j2ee", "j2se", "jdk", "jvm"],
            "spring boot": ["springboot", "spring framework"],
            "rest apis": ["restful", "rest api", "api development"],
            "microservices": ["microservice", "micro service"],
            "mysql": ["sql", "database"],
            "docker": ["containerization", "containers"],
            "devops": ["ci/cd", "continuous integration", "continuous deployment"]
        }
        
        for skill, synonyms in skill_synonyms.items():
            if skill in self.skills:
                for synonym in synonyms:
                    if synonym in full_text and skill not in matched_skills:
                        skill_score += 40 / len(self.skills)
                        matched_skills.append(skill)
                        break
        
        score += min(skill_score, 40)
        match_details["matched_skills"] = matched_skills
        match_details["missing_skills"] = missing_skills[:5]  # Top 5 missing
        
        # 2. Keyword Matching (20 points)
        keyword_matches = sum(1 for keyword in self.keywords if keyword in full_text)
        keyword_score = min((keyword_matches / len(self.keywords)) * 20, 20)
        score += keyword_score
        match_details["keyword_matches"] = keyword_matches
        
        # 3. Experience Matching (20 points)
        experience_match = True
        exp_patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*years?',
            r'minimum\s*(\d+)\s*years?',
            r'at least\s*(\d+)\s*years?'
        ]
        
        exp_text = f"{experience_required} {job_description}".lower()
        required_exp = None
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, exp_text)
            if matches:
                if isinstance(matches[0], tuple):
                    required_exp = int(matches[0][0])
                else:
                    required_exp = int(matches[0])
                break
        
        if required_exp:
            if self.experience_years >= required_exp:
                score += 20
            elif self.experience_years >= required_exp - 1:
                score += 15  # Close match
            elif self.experience_years >= required_exp - 2:
                score += 10  # Somewhat close
            else:
                experience_match = False
                score += 5  # Partial credit
        else:
            score += 15  # No explicit requirement, assume match
        
        match_details["experience_match"] = experience_match
        
        # 4. Role Title Matching (10 points)
        title_lower = job_title.lower()
        role_keywords = ["developer", "engineer", "backend", "java", "software"]
        title_match = any(kw in title_lower for kw in role_keywords)
        if title_match:
            score += 10
        
        # 5. Education Matching (10 points)
        education_keywords = ["bachelor", "btech", "b.tech", "computer science", "engineering"]
        edu_match = any(kw in full_text for kw in education_keywords)
        if edu_match:
            score += 10
        
        # Normalize score to 0-100
        final_score = min(score, 100.0)
        
        # Generate reason
        reason = self._generate_reason(final_score, match_details, required_exp)
        
        return final_score, {
            **match_details,
            "required_experience": required_exp,
            "reason": reason
        }
    
    def _generate_reason(self, score: float, details: Dict, required_exp: int = None) -> str:
        """Generate human-readable reason for match score"""
        reasons = []
        
        if score >= 80:
            reasons.append("Excellent match")
        elif score >= 70:
            reasons.append("Good match")
        elif score >= 60:
            reasons.append("Moderate match")
        else:
            reasons.append("Partial match")
        
        if details["matched_skills"]:
            reasons.append(f"Matched {len(details['matched_skills'])} skills")
        
        if details["keyword_matches"] > 0:
            reasons.append(f"Matched {details['keyword_matches']} keywords")
        
        if required_exp:
            if details["experience_match"]:
                reasons.append(f"Experience requirement met ({required_exp} years)")
            else:
                reasons.append(f"Experience gap: requires {required_exp} years")
        
        return ". ".join(reasons)
    
    def is_job_eligible(self, match_score: float, min_score: float = 70) -> bool:
        """Check if job meets minimum match criteria"""
        return match_score >= min_score
