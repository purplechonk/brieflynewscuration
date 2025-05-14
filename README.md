# News Article Evaluation Microservice

This microservice evaluates incoming news articles from newsapi.ai for their potential to generate meaningful insights. It analyzes articles based on multiple criteria including fact density, named entities, novelty, and analytical depth to determine if they warrant further analysis.

## Features

- Integration with newsapi.ai for article sourcing
- Comprehensive article evaluation using multiple metrics
- Named entity recognition and fact density analysis
- Novelty detection using zero-shot classification
- Analytical depth assessment
- Topic relevance scoring
- Sentiment analysis
- Confidence scoring for evaluation reliability

## Requirements

- Python 3.8+
- SpaCy
- PyTorch
- Transformers
- FastAPI
- NewsAPI.ai API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd news-evaluation-service
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download SpaCy model:
```bash
python -m spacy download en_core_web_sm
```

5. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Add your NewsAPI.ai API key to the `.env` file
   - Adjust other configuration options as needed

## Running the Service

Start the service using uvicorn:

```bash
uvicorn app.main:app --reload
```

The service will be available at `http://localhost:8000`

## API Endpoints

### POST /fetch-and-evaluate

Fetches articles from newsapi.ai and evaluates them for insight potential.

Example request:
```json
{
    "query": "artificial intelligence",
    "from_date": "2024-01-01T00:00:00Z",
    "to_date": "2024-01-02T00:00:00Z",
    "languages": ["eng"],
    "categories": ["technology"],
    "source_locations": ["USA"],
    "limit": 50
}
```

Example response:
```json
{
    "total_articles": 50,
    "worthy_articles": 15,
    "results": [
        {
            "article": {
                "title": "Example News Article",
                "content": "Article content...",
                "source": "News Source",
                "published_date": "2024-01-01T00:00:00Z",
                "author": "John Doe",
                "url": "https://example.com/article",
                "categories": ["technology"],
                "entities": [...],
                "image_url": "https://example.com/image.jpg",
                "language": "eng",
                "location": {...}
            },
            "evaluation": {
                "article_id": "uuid",
                "overall_score": 0.85,
                "is_worthy": true,
                "metrics": {
                    "named_entities_count": 15,
                    "fact_density_score": 0.75,
                    "novelty_score": 0.8,
                    "analytical_depth_score": 0.7,
                    "readability_score": 0.85,
                    "topic_relevance_score": 0.9,
                    "sentiment_score": 0.6
                },
                "evaluation_timestamp": "2024-01-01T00:00:00Z",
                "confidence_score": 0.85,
                "reasons": [
                    "High fact density",
                    "High novelty content",
                    "Meets overall quality threshold for further analysis"
                ]
            }
        }
    ]
}
```

### POST /evaluate

Evaluates a single article for its potential to generate meaningful insights.

Example request:
```json
{
    "title": "Example News Article",
    "content": "Article content goes here...",
    "source": "News Source",
    "published_date": "2024-01-01T00:00:00Z",
    "author": "John Doe",
    "url": "https://example.com/article",
    "categories": ["technology", "business"]
}
```

Example response:
```json
{
    "article_id": "uuid",
    "overall_score": 0.85,
    "is_worthy": true,
    "metrics": {
        "named_entities_count": 15,
        "fact_density_score": 0.75,
        "novelty_score": 0.8,
        "analytical_depth_score": 0.7,
        "readability_score": 0.85,
        "topic_relevance_score": 0.9,
        "sentiment_score": 0.6
    },
    "evaluation_timestamp": "2024-01-01T00:00:00Z",
    "confidence_score": 0.85,
    "reasons": [
        "High fact density",
        "High novelty content",
        "Meets overall quality threshold for further analysis"
    ]
}
```

### GET /health

Health check endpoint to verify service status.

## Evaluation Metrics

- **Named Entities Count**: Number of unique named entities (people, organizations, locations, etc.)
- **Fact Density Score**: Ratio of named entities to content length
- **Novelty Score**: Measures how novel or newsworthy the content is
- **Analytical Depth Score**: Evaluates the presence of analytical elements
- **Readability Score**: Measures how easy the content is to read
- **Topic Relevance Score**: Measures relevance to declared categories
- **Sentiment Score**: Analyzes the emotional tone of the content

## Configuration

### Environment Variables

- `NEWSAPI_KEY`: Your NewsAPI.ai API key (required)
- `NEWSAPI_ENDPOINT`: NewsAPI.ai API endpoint (optional)
- `DEFAULT_LANGUAGE`: Default language for article fetching (optional, default: "eng")
- `ARTICLES_LIMIT`: Maximum number of articles to fetch (optional, default: 100)

### Evaluation Thresholds

The service uses the following thresholds (configurable in `app/evaluator.py`):

- Minimum named entities: 5
- Minimum content length: 200 words
- Worthy threshold: 0.7

## Error Handling

The service returns appropriate HTTP status codes:

- 200: Successful evaluation
- 400: Invalid request format
- 500: Internal server error

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
