from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.evaluator import ArticleEvaluator
from app.models import Article, ArticleEvaluation
from app.news_api_client import NewsAPIClient, NewsAPIConfig
from app.config import settings

app = FastAPI(
    title="News Article Evaluation Service",
    description="A microservice for evaluating news articles for their potential to generate meaningful insights",
    version="1.0.0"
)

evaluator = ArticleEvaluator()

class ArticleRequest(BaseModel):
    title: str
    content: str
    source: str
    published_date: datetime
    author: Optional[str] = None
    url: str
    categories: List[str] = []

class FetchArticlesRequest(BaseModel):
    query: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    languages: List[str] = ["eng"]
    categories: Optional[List[str]] = None
    source_locations: Optional[List[str]] = None
    limit: Optional[int] = 100

async def get_news_api_client():
    config = NewsAPIConfig(
        api_key=settings.newsapi_key,
        endpoint=settings.newsapi_endpoint
    )
    async with NewsAPIClient(config) as client:
        yield client

@app.post("/evaluate", response_model=ArticleEvaluation)
async def evaluate_article(article: ArticleRequest):
    """
    Evaluate a news article for its potential to generate meaningful insights.
    Returns an evaluation score and detailed metrics.
    """
    try:
        article_obj = Article(
            title=article.title,
            content=article.content,
            source=article.source,
            published_date=article.published_date,
            author=article.author,
            url=article.url,
            categories=article.categories
        )
        evaluation = await evaluator.evaluate(article_obj)
        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch-and-evaluate")
async def fetch_and_evaluate_articles(
    request: FetchArticlesRequest,
    news_client: NewsAPIClient = Depends(get_news_api_client)
):
    """
    Fetch articles from newsapi.ai and evaluate them.
    Returns only articles that meet the evaluation criteria.
    """
    try:
        # Fetch articles from newsapi.ai
        articles = await news_client.fetch_articles(
            query=request.query,
            from_date=request.from_date,
            to_date=request.to_date,
            languages=request.languages,
            categories=request.categories,
            source_locations=request.source_locations,
            limit=request.limit or settings.articles_limit
        )

        # Evaluate each article
        evaluated_articles = []
        for article_data in articles:
            article = Article(
                title=article_data["title"],
                content=article_data["content"],
                source=article_data["source"],
                published_date=article_data["published_date"],
                author=article_data["author"],
                url=article_data["url"],
                categories=article_data["categories"]
            )
            evaluation = await evaluator.evaluate(article)
            if evaluation.is_worthy:
                evaluated_articles.append({
                    "article": article_data,
                    "evaluation": evaluation
                })

        return {
            "total_articles": len(articles),
            "worthy_articles": len(evaluated_articles),
            "results": evaluated_articles
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"} 