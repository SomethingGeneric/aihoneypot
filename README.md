# ai(honey)pot

Trapping SSH bots in LLaMA powered hell

## Features

- **TCP/SSH Honeypot Server**: Run as a network-accessible SSH-like server that accepts any credentials
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

### Interactive Shell Mode (Local)
Run the honeypot as an interactive shell on your local machine:

```bash
python bash.py
```

### TCP Server Mode (Network Honeypot)
Run as a TCP server that listens for network connections:

```bash
# Listen on all interfaces, port 2222 (default)
python bash.py --tcp

# Custom host and port
python bash.py --tcp --host 0.0.0.0 --port 22

# With specific AI provider
python bash.py --tcp --provider openai --port 2222
```

The TCP server mode:
- Mimics an OpenSSH server banner for realistic nmap scans
- Accepts ANY username/password combination (logs all attempts)
- Provides an AI-powered shell session to each connected client
- Handles multiple concurrent connections
- Logs all commands executed by connected clients

**Security Note**: When running on privileged ports (< 1024), you'll need root/sudo privileges:
```bash
sudo python bash.py --tcp --port 22
```

### Legacy LLaMA Support
```bash
python bash.py --endpoint http://localhost:11434
```

### Specify Provider
```bash
python bash.py --provider openai
```

### Standalone TCP Server
You can also run the TCP server directly:

```bash
python tcp_server.py --port 2222
```

## Docker Systems (Future Expansion)

The codebase now includes `docker_systems.py` which provides the foundation for running honeypots in Docker containers:

- Isolated container environments
- Multiple OS support (Ubuntu, CentOS, Alpine, Debian)
- Hybrid AI/real execution modes
- Container lifecycle management

## Architecture

- `bash.py`: Main entry point and shell interface (supports both interactive and TCP modes)
- `tcp_server.py`: TCP/SSH honeypot server implementation
- `config.py`: Configuration management with Pydantic models
- `providers.py`: AI provider implementations (LLaMA, OpenAI, MCP)
- `docker_systems.py`: Docker integration for future expansion
- `requirements.txt`: Python dependencies
