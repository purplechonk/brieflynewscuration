from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Article(BaseModel):
    title: str
    content: str
    source: str
    published_date: datetime
    author: Optional[str] = None
    url: str
    categories: List[str] = []

class ContentMetrics(BaseModel):
    named_entities_count: int
    fact_density_score: float
    novelty_score: float
    analytical_depth_score: float
    readability_score: float
    topic_relevance_score: float
    sentiment_score: float

class ArticleEvaluation(BaseModel):
    article_id: str
    overall_score: float
    is_worthy: bool
    metrics: ContentMetrics
    evaluation_timestamp: datetime
    confidence_score: float
    reasons: List[str] 