# GitHub Bounty API

A FastAPI application for searching and discovering GitHub bounty programs and issues.

## Features

- 🔍 Search GitHub issues with bounty-related labels
- 📋 List known bug bounty platforms
- 📖 Interactive API documentation (Swagger UI and ReDoc)
- 🚀 Ready for deployment on Render
- 🔐 Optional GitHub API token support for higher rate limits

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd github-bounty-api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the example environment file and configure:
```bash
cp .env.example .env
# Edit .env and add your GitHub token (optional but recommended)
```

5. Run the application:
```bash
uvicorn main:app --reload
```

The API will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Root
- `GET /` - API information
- `GET /health` - Health check

### Search
- `GET /api/search/issues` - Search bounty issues
  - Query parameters:
    - `query`: Search query string
    - `labels`: Comma-separated list of labels
    - `language`: Programming language filter
    - `state`: Issue state (open/closed, default: open)
    - `per_page`: Results per page (1-100, default: 30)
    - `page`: Page number (default: 1)

### Programs
- `GET /api/programs` - List known bounty programs

## Deployment

### Deploy to Render

1. Fork this repository
2. Sign up for a [Render account](https://render.com)
3. Create a new Web Service
4. Connect your GitHub repository
5. Use the following configuration:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables in Render dashboard:
   - `GITHUB_TOKEN` (optional but recommended)
7. Deploy!

The `render.yaml` file in this repository can also be used for automatic configuration.

## GitHub API Token

While the API works without a token, GitHub's rate limit for unauthenticated requests is 60 requests per hour. For higher limits (5000 requests per hour), create a personal access token:

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `public_repo` (read-only access)
4. Generate and copy the token
5. Add it to your `.env` file or Render environment variables

## License

MIT
