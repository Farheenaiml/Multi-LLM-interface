# Multi-LLM Broadcast Workspace Backend

FastAPI backend for the Multi-LLM Broadcast Workspace application, providing real-time streaming communication with multiple LLM providers.

## Features

- **Multi-Provider Support**: Integrates with LiteLLM, Google Data Studio, and Groq AI
- **Real-time Streaming**: WebSocket-based streaming for live response updates
- **Session Management**: Persistent conversation sessions with multiple panes
- **Content Transfer**: Send messages between different model conversations
- **Summarization**: Generate summaries across multiple conversations
- **Metrics Tracking**: Real-time token usage, cost, and latency monitoring
- **Error Handling**: Robust error handling with retry logic and graceful degradation

## Architecture

### Core Components

- **FastAPI Application** (`main.py`): REST API endpoints and WebSocket server
- **Broadcast Orchestrator** (`broadcast_orchestrator.py`): Coordinates multi-provider requests
- **Session Manager** (`session_manager.py`): Manages session state and persistence
- **LLM Adapters** (`adapters/`): Provider-specific integrations
- **Data Models** (`models.py`): Pydantic models for type safety

### API Endpoints

#### Core Endpoints
- `GET /health` - Health check with provider status
- `POST /broadcast` - Create broadcast to multiple models
- `POST /send-to` - Transfer content between panes
- `POST /summarize` - Generate summaries of conversations
- `WS /ws/{session_id}` - WebSocket for real-time streaming

#### Management Endpoints
- `GET /sessions` - List sessions with pagination
- `GET /sessions/{session_id}` - Get session details
- `DELETE /sessions/{session_id}` - Delete session
- `GET /models` - Get available models from all providers
- `GET /providers/health` - Check provider health status
- `GET /stats` - Get system statistics

## Setup

### Prerequisites

- Python 3.8+
- pip or conda for package management

### Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start the server**:
   ```bash
   python start.py
   ```

   Or directly with uvicorn:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8080 --reload
   ```

### Environment Variables

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8080
RELOAD=true
LOG_LEVEL=info

# LiteLLM Configuration
LITELLM_BASE_URL=http://localhost:8000
LITELLM_MASTER_KEY=sk-1234

# Google API Configuration
GOOGLE_API_KEY=your_google_api_key
GOOGLE_BASE_URL=https://generativelanguage.googleapis.com/v1beta

# Groq API Configuration
GROQ_API_KEY=your_groq_api_key
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

## Usage

### Basic Broadcast Request

```python
import httpx
import asyncio

async def test_broadcast():
    async with httpx.AsyncClient() as client:
        # Create broadcast request
        response = await client.post("http://localhost:8080/broadcast", json={
            "prompt": "Explain quantum computing in simple terms",
            "models": [
                {"provider_id": "litellm", "model_id": "gpt-3.5-turbo"},
                {"provider_id": "groq", "model_id": "mixtral-8x7b-32768"}
            ],
            "session_id": "test-session"
        })
        
        print(f"Broadcast started: {response.json()}")

asyncio.run(test_broadcast())
```

### WebSocket Streaming

```javascript
// Frontend WebSocket connection
const ws = new WebSocket('ws://localhost:8080/ws/test-session');

ws.onmessage = (event) => {
    const streamEvent = JSON.parse(event.data);
    
    switch (streamEvent.type) {
        case 'token':
            // Handle streaming token
            console.log(`Token: ${streamEvent.data.token}`);
            break;
        case 'final':
            // Handle final response
            console.log(`Final: ${streamEvent.data.content}`);
            break;
        case 'meter':
            // Handle metrics
            console.log(`Metrics: ${streamEvent.data.tokens_used} tokens, $${streamEvent.data.cost}`);
            break;
        case 'error':
            // Handle errors
            console.error(`Error: ${streamEvent.data.message}`);
            break;
    }
};
```

## Testing

### Run Basic Tests

```bash
python test_basic.py
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8080/health

# Get available models
curl http://localhost:8080/models

# Check provider health
curl http://localhost:8080/providers/health
```

## Development

### Project Structure

```
backend/
├── main.py                 # FastAPI application
├── models.py              # Pydantic data models
├── broadcast_orchestrator.py  # Multi-provider coordination
├── session_manager.py     # Session state management
├── start.py              # Startup script
├── test_basic.py         # Basic functionality tests
├── requirements.txt      # Python dependencies
├── adapters/             # LLM provider adapters
│   ├── __init__.py
│   ├── base.py          # Abstract base adapter
│   ├── registry.py      # Adapter registry
│   ├── litellm_adapter.py   # LiteLLM integration
│   ├── google_adapter.py    # Google Data Studio integration
│   └── groq_adapter.py      # Groq AI integration
└── README.md            # This file
```

### Adding New Providers

1. Create a new adapter class inheriting from `LLMAdapter`
2. Implement the `stream()` and `get_models()` methods
3. Register the adapter in `registry.py`
4. Add configuration variables to environment setup

### Error Handling

The backend implements comprehensive error handling:

- **Rate Limiting**: Exponential backoff with jitter
- **Timeouts**: Configurable timeouts with graceful degradation
- **Provider Failures**: Continues with available providers
- **WebSocket Disconnections**: Automatic reconnection logic
- **Validation Errors**: Clear error messages with suggestions

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["python", "start.py"]
```

### Production Considerations

- Use a production WSGI server (gunicorn + uvicorn workers)
- Set up proper logging and monitoring
- Configure rate limiting and request size limits
- Use environment-specific configuration
- Set up health checks and graceful shutdown
- Consider using Redis for session persistence
- Implement proper API key management

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and Python path is correct
2. **Provider Connection Failures**: Check API keys and network connectivity
3. **WebSocket Disconnections**: Verify CORS settings and connection handling
4. **High Memory Usage**: Monitor session cleanup and implement limits
5. **Rate Limiting**: Implement proper backoff strategies for each provider

### Logging

The application uses structured logging with different levels:

- `INFO`: General application flow
- `WARNING`: Recoverable issues
- `ERROR`: Serious problems requiring attention
- `DEBUG`: Detailed debugging information

### Monitoring

Key metrics to monitor:

- Active WebSocket connections
- Session count and memory usage
- Provider response times and error rates
- Token usage and costs
- Request queue lengths

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints for all functions
3. Include docstrings for public methods
4. Write tests for new functionality
5. Update documentation as needed

## License

This project is part of the Multi-LLM Broadcast Workspace application.