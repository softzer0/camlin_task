# Currency Wallet API

FastAPI-based REST API that tracks foreign currency holdings with real-time PLN conversion using NBP (National Bank of Poland) exchange rates.

## Features

- Real-time currency conversion using NBP API
- JWT authentication
- MongoDB for wallet persistence
- Redis for caching
- Docker and Docker Compose setup
- Async operations
- Full test coverage

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/currency-wallet.git
cd currency-wallet
```

2. Configure environment:

```bash
cp .env.example .env
```

3. Start services:

```bash
# Development
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Production
docker-compose up -d
```

## API Usage

### Authentication

```bash
# Get token
curl -X POST "http://localhost:8000/api/v1/auth/token" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password"}'
```

### Wallet Operations

```bash
# Get wallet status
curl -X GET "http://localhost:8000/api/v1/wallet" \
     -H "Authorization: Bearer YOUR_TOKEN"

# Add funds
curl -X POST "http://localhost:8000/api/v1/wallet/add" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"currency": "EUR", "amount": "100.00"}'

# Subtract funds
curl -X POST "http://localhost:8000/api/v1/wallet/subtract" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"currency": "EUR", "amount": "50.00"}'
```

## Development

```bash
# Install dependencies
poetry install

# Run tests
poetry run pytest

# Lint code
poetry run ruff check .

# Format code
poetry run black .
```

## Project Structure

```
app/
├── api/            # API endpoints
│   └── v1/
├── core/           # Core functionality
├── models/         # Pydantic models
├── services/       # Business logic
└── repositories/   # Data access
```

## Configuration

Key environment variables:

```bash
MONGODB_URL=mongodb://mongodb:27017/wallet_app
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-secret-key
```

See `.env.example` for all available options.

## Testing

Run tests with:

```bash
# All tests
poetry run pytest

# With coverage
poetry run pytest --cov=app

# Specific test
poetry run pytest tests/test_api.py -v
```
