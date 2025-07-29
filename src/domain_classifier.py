#!/usr/bin/env python3
import requests
import json
import sqlite3
import logging
import re
from typing import Dict, Optional
from datetime import datetime

class DomainClassifier:
    def __init__(self, db_path: str = '../data/smartguard.db'):
        self.db_path = db_path
        self.ollama_url = "http://localhost:11434/api/generate"
        self.categories = {
            "educational": {"color": "green", "risk": "low"},
            "entertainment": {"color": "blue", "risk": "low"},
            "social_media": {"color": "yellow", "risk": "medium"},
            "gaming": {"color": "orange", "risk": "medium"},
            "inappropriate": {"color": "red", "risk": "high"}
        }
        self.logger = logging.getLogger(__name__)

    def get_classification_prompt(self, domain: str) -> str:
        return f"Classify the domain {domain} into one of the following categories: educational, entertainment, social_media, gaming, inappropriate. Only respond with the category name."

    def classify_domain(self, domain: str) -> Dict[str, any]:
        try:
            # Check cached result first
            cached_result = self.get_cached_classification(domain)
            if cached_result:
                return cached_result

            # Handle known risky domains (manual override)
            known_inappropriate = ["pornhub.com", "xvideos.com", "redtube.com", "xnxx.com"]
            if domain in known_inappropriate:
                return self.cache_and_return(domain, "inappropriate", 0.85)

            # Generate classification via Ollama
            prompt = self.get_classification_prompt(domain)
            payload = {
                "model": "tinyllama:latest",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.0,
                    "top_p": 0.9,
                    "max_tokens": 20
                }
            }

            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()

            raw = result.get("response", "").strip().lower()
            print(f"[DEBUG] Ollama response for {domain}: {raw}")

            # Extract category using regex from response
            match = re.search(r'\b(educational|entertainment|social_media|gaming|inappropriate)\b', raw)
            category = match.group(1) if match else "entertainment"

            confidence = 0.85 if category in ["educational", "inappropriate"] else 0.75
            return self.cache_and_return(domain, category, confidence)

        except Exception as e:
            self.logger.error(f"Classification error for {domain}: {e}")
            return self.cache_and_return(domain, "entertainment", 0.5)

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
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT category, confidence, risk_level, color, timestamp
                FROM domain_classifications 
                WHERE domain = ? AND timestamp > datetime('now', '-7 days')
            ''', (domain,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return {
                    "domain": domain,
                    "category": result[0],
                    "confidence": result[1],
                    "risk_level": result[2],
                    "color": result[3],
                    "timestamp": result[4]
                }
            return None
        except Exception as e:
            self.logger.error(f"Cache lookup error: {e}")
            return None

    def cache_classification(self, classification: Dict):
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
                classification["domain"],
                classification["category"],
                classification["confidence"],
                classification["risk_level"],
                classification["color"],
                classification["timestamp"]
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Cache store error: {e}")

if __name__ == '__main__':
    classifier = DomainClassifier()
    test_domains = [
        "facebook.com",
        "xvideos.com",
        "pornhub.com",
        "minecraft.net",
        "google.com"
    ]
    for domain in test_domains:
        result = classifier.classify_domain(domain)
        print(f"{domain} -> {result['category']} ({result['confidence']:.2f})")
