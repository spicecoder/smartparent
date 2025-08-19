#!/usr/bin/env python3
import sqlite3
import logging
import requests
from typing import Dict, Optional
from datetime import datetime

class DomainClassifier:
    def __init__(self, db_path: str = '../data/smartguard.db', ollama_host: str = "http://192.168.29.42:11434"):
        self.db_path = db_path
        self.ollama_url = f"{ollama_host}/api/generate"
        self.model = "llama3"
        self.categories = {
            "educational": {"color": "green", "risk": "low"},
            "entertainment": {"color": "blue", "risk": "low"},
            "social_media": {"color": "yellow", "risk": "medium"},
            "gaming": {"color": "orange", "risk": "medium"},
            "shopping": {"color": "purple", "risk": "medium"},
            "inappropriate": {"color": "red", "risk": "high"},
            "unknown": {"color": "gray", "risk": "unknown"},
        }
        self.logger = logging.getLogger(__name__)

    def classify_domain(self, domain: str) -> Dict[str, any]:
       
        try:
            prompt = f"""
You are a domain classifier. Classify each domain into one of these categories:
- educational
- entertainment
- social_media
- gaming
- shopping
- inappropriate
- unknown

Return only the category name in lowercase.

Here are some examples:
khanacademy.org -> educational
coursera.org -> educational
udemy.com -> educational
edx.org -> educational

netflix.com -> entertainment
spotify.com -> entertainment
hulu.com -> entertainment

facebook.com -> social_media
twitter.com -> social_media
snapchat.com -> social_media
stackoverflow.com -> social_media

minecraft.net -> gaming
steampowered.com -> gaming
epicgames.com -> gaming

amazon.com -> shopping
bestbuy.com -> shopping
myntra.com -> shopping

pornhub.com -> inappropriate
redtube.com -> inappropriate
xnxx.com -> inappropriate

If you're not sure, make the most reasonable guess based on domain name and context.


Now classify: {domain}
"""
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=120
            )
            response.raise_for_status()
            category = response.json().get("response", "").strip().lower()

            if category not in self.categories:
                category = "unknown"

            confidence = 0.85 if category in ["inappropriate", "educational"] else 0.75

            result = {
                "domain": domain,
                "category": category,
                "confidence": confidence,
                "risk_level": self.categories[category]["risk"],
                "color": self.categories[category]["color"],
                "timestamp": datetime.now().isoformat()
            }

            self.cache_classification(result)
            return result

        except Exception as e:
            self.logger.error(f"LLaMA3 error for {domain}: {e}")
            return self.cache_and_return(domain, "unknown", 0.5)

    def cache_and_return(self, domain: str, category: str, confidence: float) -> Dict:
        classification = {
            "domain": domain,
            "category": category,
            "confidence": confidence,
            "risk_level": self.categories[category]["risk"],
            "color": self.categories[category]["color"],
            "timestamp": datetime.now().isoformat()
        }
        self.cache_classification(classification)
        return classification

    def get_cached_classification(self, domain: str) -> Optional[Dict]:
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, confidence, risk_level, color, timestamp
                FROM domain_classifications
                WHERE domain = ? AND timestamp > datetime('now', '-7 days')
            ''', (domain,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return {
                    "domain": domain,
                    "category": row[0],
                    "confidence": row[1],
                    "risk_level": row[2],
                    "color": row[3],
                    "timestamp": row[4]
                }
            return None
        except Exception as e:
            self.logger.error(f"Cache lookup error: {e}")
            return None

    def cache_classification(self, data: Dict):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS domain_classifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    risk_level TEXT NOT NULL,
                    color TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT OR REPLACE INTO domain_classifications
                (domain, category, confidence, risk_level, color, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data["domain"],
                data["category"],
                data["confidence"],
                data["risk_level"],
                data["color"],
                data["timestamp"]
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Cache store error: {e}")

if __name__ == '__main__':
    classifier = DomainClassifier()
    test_domains = [
        "www.sydney.edu.au", "futurelearn.com",              # educational
    "crunchyroll.com", "primevideo.com",             # entertainment
    "pinterest.com", "threads.net",                  # social_media
    "ign.com", "gamepedia.com",                      # gaming
    "nykaa.com", "ajio.com",                         # shopping
    "spankbang.com", "hclips.com",                   # inappropriate
    "replit.com", "archive.org"  
    ]
    for domain in test_domains:
        result = classifier.classify_domain(domain)
        print(f"{domain} -> {result['category']} ({result['confidence']:.2f})")
