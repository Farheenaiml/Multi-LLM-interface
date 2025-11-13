# Multi-LLM Broadcast Workspace

A browser-based application that enables users to simultaneously prompt multiple Large Language Models (LLMs), stream responses in parallel panes, compare outputs, route context between conversations, and monitor real-time cost and latency metrics.

## Features

- **Broadcast Prompts**: Send the same prompt to multiple LLM providers simultaneously
- **Real-time Streaming**: View responses as they stream in parallel panes
- **Response Comparison**: Compare outputs with diff highlighting
- **Content Transfer**: Route messages between conversations with provenance tracking
- **Metrics Monitoring**: Track token usage, costs, and latency in real-time
- **Pipeline Templates**: Create reusable workflows from conversation sequences
- **Conversation History**: Persist and manage conversation history

## Architecture

- **Frontend**: React 18 + TypeScript 5 + Vite 5 + Zustand
- **Backend**: FastAPI + Python 3.11 + WebSockets
- **LLM Integration**: LiteLLM service + direct provider APIs
- **Database**: PostgreSQL (optional) + Redis (optional)
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- Docker and Docker Compose

### Development Setup

1. Clone the repository
2. Copy environment configuration:
   ```bash
   cp backend/.env.example backend/.env
   ```
3. Add your LLM provider API keys to `backend/.env`
4. Start the development environment:
   ```bash
   docker-compose up -d
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8080
- LiteLLM Service: http://localhost:8000

### Manual Setup (without Docker)

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Supported LLM Providers

- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude-3 Opus, Sonnet)
- Google (Gemini Pro)
- Groq (Mixtral-8x7B)

## Configuration

### Environment Variables

See `backend/.env.example` for all available configuration options.

### LiteLLM Configuration

Edit `litellm_config.yaml` to configure model access and provider settings.

## Development

### Project Structure

```
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── types/           # TypeScript interfaces
│   │   └── ...
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── main.py              # Application entry point
│   ├── models.py            # Pydantic data models
│   └── requirements.txt
├── database/                 # Database initialization
├── docker-compose.yml        # Development environment
└── litellm_config.yaml      # LLM provider configuration
```

### API Documentation

Once the backend is running, visit http://localhost:8080/docs for interactive API documentation.

## License

MIT License