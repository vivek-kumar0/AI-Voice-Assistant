"""
news.py
--------
Fetches the latest news headlines using the NewsAPI.org service.
"""

import os
import requests
from utils.logger import get_logger

logger = get_logger(__name__)


class NewsService:
    """Client for retrieving top news headlines."""

    BASE_URL = "https://newsapi.org/v2/top-headlines"

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY")

    def get_top_headlines(self, country: str = "in", count: int = 5) -> str:
        """
        Retrieve the top news headlines for a given country code.

        Args:
            country (str): Two-letter country code, e.g. "in", "us".
            count (int): Number of headlines to return.

        Returns:
            str: A spoken-friendly summary of top headlines.
        """
        if not self.api_key:
            return "News service is not configured. Please add a NewsAPI key."

        params = {"apiKey": self.api_key, "country": country, "pageSize": count}

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            articles = data.get("articles", [])

            if not articles:
                return "I couldn't find any news headlines right now."

            headlines = [article["title"] for article in articles[:count]]
            summary = "Here are the top headlines: " + "; ".join(headlines)
            return summary

        except requests.exceptions.RequestException as e:
            logger.error(f"News API request failed: {e}")
            return "Sorry, I couldn't connect to the news service right now."
