import os
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dateutil.parser import parse
from pydantic import BaseModel

class NewsAPIConfig(BaseModel):
    api_key: str
    endpoint: str = "https://api.newsapi.ai/api/v1/article/getArticles"

class NewsAPIClient:
    def __init__(self, config: NewsAPIConfig):
        self.config = config
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def fetch_articles(
        self,
        query: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        languages: List[str] = ["eng"],
        categories: List[str] = None,
        source_locations: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Fetch articles from newsapi.ai based on specified criteria
        """
        params = {
            "apiKey": self.config.api_key,
            "articlesSortBy": "date",
            "articlesCount": limit,
            "articlesSortByAsc": False,
            "includeArticleCategories": True,
            "includeArticleImage": True,
            "includeArticleBasicInfo": True,
            "includeArticleLocation": True,
            "includeArticleEntities": True,
            "language": ",".join(languages),
        }

        if query:
            params["q"] = query

        if from_date:
            params["dateStart"] = from_date.strftime("%Y-%m-%d")
        
        if to_date:
            params["dateEnd"] = to_date.strftime("%Y-%m-%d")

        if categories:
            params["categoryUri"] = ",".join(categories)

        if source_locations:
            params["sourceLocationUri"] = ",".join(source_locations)

        try:
            async with self.session.get(self.config.endpoint, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"NewsAPI request failed: {error_text}")
                
                data = await response.json()
                return self._process_articles(data)
        except Exception as e:
            raise Exception(f"Error fetching articles from NewsAPI: {str(e)}")

    def _process_articles(self, api_response: Dict) -> List[Dict]:
        """
        Process the raw API response and convert it to our internal format
        """
        articles = []
        for article in api_response.get("articles", {}).get("results", []):
            processed_article = {
                "title": article.get("title", ""),
                "content": article.get("body", ""),
                "source": article.get("source", {}).get("title", ""),
                "published_date": parse(article.get("dateTime", "")),
                "author": article.get("author", ""),
                "url": article.get("url", ""),
                "categories": [
                    cat.get("label", "")
                    for cat in article.get("categories", [])
                    if cat.get("label")
                ],
                "entities": article.get("entities", []),
                "image_url": article.get("image", ""),
                "language": article.get("language", ""),
                "location": article.get("location", {}),
            }
            articles.append(processed_article)
        return articles 