import requests
import wikipedia
from urllib.parse import quote_plus
from app.core.config import settings

def weather(city: str) -> str:
    if not settings.openweather_api_key:
        return "Weather is not configured. Add OPENWEATHER_API_KEY to the backend environment."
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": settings.openweather_api_key, "units": "metric"},
            timeout=8,
        )
        r.raise_for_status()
        d = r.json()
        return f"Weather in {city}: {d['weather'][0]['description']}, {d['main']['temp']}°C, feels like {d['main']['feels_like']}°C, humidity {d['main']['humidity']}%."
    except Exception:
        return f"I couldn't retrieve weather for {city} right now."

def news() -> str:
    if not settings.news_api_key:
        return "News is not configured. Add NEWS_API_KEY to the backend environment."
    try:
        r = requests.get(
            "https://newsapi.org/v2/top-headlines",
            params={"apiKey": settings.news_api_key, "country": "in", "pageSize": 5},
            timeout=8,
        )
        r.raise_for_status()
        articles = r.json().get("articles", [])
        if not articles:
            return "No headlines were returned."
        return "Top headlines: " + "; ".join(a.get("title", "") for a in articles[:5])
    except Exception:
        return "I couldn't retrieve news right now."

def wikipedia_summary(query: str) -> str:
    try:
        return f"According to Wikipedia: {wikipedia.summary(query, sentences=2)}"
    except wikipedia.exceptions.DisambiguationError:
        return f"That topic is ambiguous. Please be more specific about {query}."
    except Exception:
        return f"I couldn't find a Wikipedia summary for {query}."

def dictionary_definition(word: str) -> str:
    try:
        r = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote_plus(word)}", timeout=8)
        if r.status_code != 200:
            return f"I couldn't find a definition for {word}."
        d = r.json()[0]
        definition = d["meanings"][0]["definitions"][0]["definition"]
        return f"{word.capitalize()} means: {definition}"
    except Exception:
        return f"I couldn't retrieve a definition for {word}."
