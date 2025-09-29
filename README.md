# ai(honey)pot

Trapping SSH bots in LLaMA powered hell

## Features

- **Multiple AI Providers**: Support for LLaMA/Ollama, OpenAI, and MCP (Model Context Protocol)
- **Docker Integration**: Foundation for running honeypots in isolated containers (future expansion)
- **Flexible Configuration**: Environment-based configuration for different providers
- **Backward Compatibility**: Maintains compatibility with existing LLaMA setups

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and configure your preferred AI provider:

```bash
cp .env.example .env
```

### Provider Options

#### LLaMA/Ollama (Default)
```env
AI_PROVIDER=llama
LLAMA_ENDPOINT=http://localhost:11434
LLAMA_MODEL=llama3.2
```

#### OpenAI
```env
AI_PROVIDER=openai
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

#### MCP (Model Context Protocol)
```env
AI_PROVIDER=mcp
MCP_SERVER_PATH=/path/to/mcp/server
MCP_SERVER_ARGS=--arg1 value1
```

## Usage

### Basic Usage
```bash
python bash.py
```

### Legacy LLaMA Support
```bash
python bash.py --endpoint http://localhost:11434
```

### Specify Provider
```bash
python bash.py --provider openai
```

## Docker Systems (Future Expansion)

The codebase now includes `docker_systems.py` which provides the foundation for running honeypots in Docker containers:

- Isolated container environments
- Multiple OS support (Ubuntu, CentOS, Alpine, Debian)
- Hybrid AI/real execution modes
- Container lifecycle management

## Architecture

- `bash.py`: Main entry point and shell interface
- `config.py`: Configuration management with Pydantic models
- `providers.py`: AI provider implementations (LLaMA, OpenAI, MCP)
- `docker_systems.py`: Docker integration for future expansion
- `requirements.txt`: Python dependencies
