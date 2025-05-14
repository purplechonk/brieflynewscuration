import spacy
import torch
from transformers import pipeline
from datetime import datetime
import uuid
import numpy as np
from typing import List, Tuple
from app.models import Article, ArticleEvaluation, ContentMetrics

class ArticleEvaluator:
    def __init__(self):
        # Load NLP models and tools
        self.nlp = spacy.load("en_core_web_sm")
        self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.zero_shot_classifier = pipeline("zero-shot-classification")
        
        # Define evaluation thresholds
        self.MIN_NAMED_ENTITIES = 5
        self.MIN_CONTENT_LENGTH = 200
        self.WORTHY_THRESHOLD = 0.7

    async def evaluate(self, article: Article) -> ArticleEvaluation:
        """
        Evaluate an article and return comprehensive evaluation metrics.
        """
        # Extract named entities
        doc = self.nlp(article.content)
        named_entities = [ent for ent in doc.ents]
        
        # Calculate basic metrics
        metrics = await self._calculate_metrics(article, doc, named_entities)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(metrics)
        
        # Determine if the article is worthy of further analysis
        is_worthy = overall_score >= self.WORTHY_THRESHOLD
        
        # Generate reasons for the evaluation
        reasons = self._generate_evaluation_reasons(metrics, overall_score)
        
        return ArticleEvaluation(
            article_id=str(uuid.uuid4()),
            overall_score=overall_score,
            is_worthy=is_worthy,
            metrics=metrics,
            evaluation_timestamp=datetime.utcnow(),
            confidence_score=self._calculate_confidence_score(metrics),
            reasons=reasons
        )

    async def _calculate_metrics(self, article: Article, doc, named_entities: List) -> ContentMetrics:
        """
        Calculate various metrics for article evaluation.
        """
        # Named entities analysis
        named_entities_count = len(named_entities)
        
        # Calculate fact density (ratio of named entities to content length)
        fact_density = named_entities_count / (len(doc) + 1)
        
        # Analyze novelty using zero-shot classification
        novelty_score = await self._analyze_novelty(article.content)
        
        # Calculate analytical depth
        analytical_depth = self._calculate_analytical_depth(doc)
        
        # Calculate readability score
        readability = self._calculate_readability_score(doc)
        
        # Analyze topic relevance
        topic_relevance = await self._analyze_topic_relevance(article)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(article.content)
        
        return ContentMetrics(
            named_entities_count=named_entities_count,
            fact_density_score=float(fact_density),
            novelty_score=float(novelty_score),
            analytical_depth_score=float(analytical_depth),
            readability_score=float(readability),
            topic_relevance_score=float(topic_relevance),
            sentiment_score=float(sentiment)
        )

    async def _analyze_novelty(self, content: str) -> float:
        """
        Analyze the novelty of the content using zero-shot classification.
        """
        labels = ["breaking news", "common knowledge", "analysis", "opinion"]
        result = self.zero_shot_classifier(content, labels)
        scores = result['scores']
        return scores[0] * 0.7 + scores[2] * 0.3  # Weight breaking news and analysis more heavily

    def _calculate_analytical_depth(self, doc) -> float:
        """
        Calculate the analytical depth based on linguistic features.
        """
        # Count analytical indicators (causal relationships, comparisons, etc.)
        analytical_indicators = len([token for token in doc 
                                  if token.dep_ in ['because', 'therefore', 'however', 'moreover']])
        return min(1.0, analytical_indicators / 10)

    def _calculate_readability_score(self, doc) -> float:
        """
        Calculate readability score using linguistic features.
        """
        sentences = len(list(doc.sents))
        words = len([token for token in doc if not token.is_punct])
        avg_sentence_length = words / max(1, sentences)
        return 1.0 - min(1.0, (avg_sentence_length - 10) / 30)

    async def _analyze_topic_relevance(self, article: Article) -> float:
        """
        Analyze the relevance of the article to its declared categories.
        """
        if not article.categories:
            return 0.5
        
        result = self.zero_shot_classifier(
            article.content,
            article.categories
        )
        return max(result['scores'])

    def _analyze_sentiment(self, content: str) -> float:
        """
        Analyze the sentiment of the content.
        """
        result = self.sentiment_analyzer(content[:512])[0]  # Limit content length for efficiency
        return result['score']

    def _calculate_overall_score(self, metrics: ContentMetrics) -> float:
        """
        Calculate the overall worthiness score based on all metrics.
        """
        weights = {
            'named_entities': 0.2,
            'fact_density': 0.2,
            'novelty': 0.15,
            'analytical_depth': 0.2,
            'readability': 0.1,
            'topic_relevance': 0.1,
            'sentiment': 0.05
        }
        
        score = (
            weights['named_entities'] * min(1.0, metrics.named_entities_count / 20) +
            weights['fact_density'] * metrics.fact_density_score +
            weights['novelty'] * metrics.novelty_score +
            weights['analytical_depth'] * metrics.analytical_depth_score +
            weights['readability'] * metrics.readability_score +
            weights['topic_relevance'] * metrics.topic_relevance_score +
            weights['sentiment'] * abs(metrics.sentiment_score)  # Use absolute value for sentiment
        )
        
        return min(1.0, max(0.0, score))

    def _calculate_confidence_score(self, metrics: ContentMetrics) -> float:
        """
        Calculate confidence in the evaluation based on metrics stability.
        """
        scores = [
            metrics.fact_density_score,
            metrics.novelty_score,
            metrics.analytical_depth_score,
            metrics.topic_relevance_score
        ]
        return 1.0 - np.std(scores)

    def _generate_evaluation_reasons(self, metrics: ContentMetrics, overall_score: float) -> List[str]:
        """
        Generate human-readable reasons for the evaluation score.
        """
        reasons = []
        
        if metrics.named_entities_count < self.MIN_NAMED_ENTITIES:
            reasons.append("Low number of named entities")
        
        if metrics.fact_density_score > 0.7:
            reasons.append("High fact density")
        elif metrics.fact_density_score < 0.3:
            reasons.append("Low fact density")
            
        if metrics.novelty_score > 0.7:
            reasons.append("High novelty content")
        elif metrics.novelty_score < 0.3:
            reasons.append("Low novelty content")
            
        if metrics.analytical_depth_score > 0.7:
            reasons.append("Strong analytical depth")
        elif metrics.analytical_depth_score < 0.3:
            reasons.append("Lacks analytical depth")
            
        if overall_score >= self.WORTHY_THRESHOLD:
            reasons.append("Meets overall quality threshold for further analysis")
        
        return reasons 