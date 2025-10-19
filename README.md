# X Algorithm Simulator

A web application that simulates Elon's X recommendation algorithm using xAI's Grok API. Enter your X username to get personalized topic recommendations based on AI-powered analysis of your activity.

## Features

- **Username Input**: Enter any X (Twitter) username
- **AI-Powered Analysis**: Uses Grok models to analyze user activity
- **Topic Extraction**: Identifies main interests and topics
- **Recommendation Simulation**: Generates personalized content recommendations
- **Modern UI**: Built with Next.js, Shadcn UI, and Tailwind CSS

## Tech Stack

- **Frontend**: Next.js 15, React, TypeScript, Shadcn UI, Tailwind CSS
- **Backend**: Python, FastAPI, xAI SDK
- **AI Models**: grok-4-fast (search/analysis), grok-code-fast-1 (algorithm simulation)

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- xAI API key (get from [xAI](https://x.ai))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd algo-x
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   pip install -r requirements.txt
   pip install -e ../xai-sdk-python
   ```

3. **Environment Variables**
   Create `.env` in the backend directory:
   ```
   XAI_API_KEY=your_xai_api_key_here
   ```

4. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Running Locally

From the root directory:

```bash
npm run dev
```

This will start both the frontend (http://localhost:3000) and backend (http://localhost:8000) simultaneously.

**Manual Start (Alternative):**

1. **Start Backend**
   ```bash
   cd backend
   # Activate venv if not already
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Browser**
   Navigate to `http://localhost:3000`

## API Documentation

### POST /analyze

Analyze a user's X activity and return recommendations.

**Request:**
```json
{
  "username": "elonmusk"
}
```

**Response:**
```json
{
  "topics": ["AI", "Space", "Technology"],
  "recommendations": "Based on your interests..."
}
```

**Error Response:**
```json
{
  "detail": "Error message"
}
```

## Deployment

### Frontend (Vercel)

1. Push to GitHub
2. Connect to Vercel
3. Deploy automatically

### Backend (Heroku)

1. Create Heroku app
2. Set environment variables
3. Deploy with git push

## Development

### Running Tests

```bash
cd backend
pytest test_main.py -v
```

### Building Frontend

```bash
cd frontend
npm run build
```

## Architecture

- **Frontend**: Single-page app with form input and results display
- **Backend**: REST API with AI integration
- **AI Flow**:
  1. Search X for user activity using grok-4-fast
  2. Extract topics from results
  3. Generate recommendations using grok-code-fast-1

## Security Considerations

- API keys stored securely in environment variables
- Input validation on both frontend and backend
- CORS configured for local development
- Rate limiting can be added for production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes
4. Run tests
5. Submit pull request

## License

MIT License - see LICENSE file for details