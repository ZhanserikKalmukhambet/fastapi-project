# OnAI Webhook Service

A FastAPI-based webhook service that processes incoming requests using LLM models and sends responses to callback URLs.

## Features

- Webhook endpoint for receiving requests
- Async processing using background tasks
- LLM integration via OpenRouter
- Response callbacks
- Message history support
- Redis-based caching
- PostgreSQL for data persistence

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd onai
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Start the services:
- PostgreSQL database
- Redis server
- Celery worker (coming soon)

6. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Webhook Endpoint

Send POST requests to `/api/v1/webhook` with the following payload:

```json
{
    "message": "Your message to process",
    "callback_url": "https://your-callback-url.com/endpoint"
}
```

## Environment Variables

Key environment variables:
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `POSTGRES_*`: Database configuration
- `REDIS_*`: Redis configuration
- `CELERY_*`: Celery configuration (coming soon)

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt  # Coming soon
```

2. Run tests:
```bash
pytest  # Coming soon
```

## License

[MIT License](LICENSE)
