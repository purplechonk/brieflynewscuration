import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    newsapi_key: str = os.getenv("NEWSAPI_KEY", "")
    newsapi_endpoint: str = os.getenv("NEWSAPI_ENDPOINT", "https://api.newsapi.ai/api/v1/article/getArticles")
    default_language: str = os.getenv("DEFAULT_LANGUAGE", "eng")
    articles_limit: int = int(os.getenv("ARTICLES_LIMIT", "100"))

settings = Settings() 