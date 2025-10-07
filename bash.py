import requests
import argparse
import os
from threading import Lock
from typing import Optional
from config import load_config, ProviderType
from providers import create_provider, BaseProvider

class BashShell:
    def __init__(self, endpoint: Optional[str] = None, provider: Optional[str] = None):
        self.lock = Lock()
        self.provider = self._initialize_provider(endpoint, provider)

    def _initialize_provider(self, endpoint: Optional[str], provider_type: Optional[str]) -> BaseProvider:
        """Initialize the appropriate provider based on configuration."""
        # Handle legacy endpoint parameter for backward compatibility
        if endpoint:
            from config import LlamaConfig
            from providers import LlamaProvider
            return LlamaProvider(LlamaConfig(endpoint=endpoint))
        
        # Load configuration and create provider
        config = load_config()
        
        # Override provider if specified
        if provider_type:
            config.provider = ProviderType(provider_type)
        
        provider_configs = {
            ProviderType.LLAMA: config.llama.dict() if config.llama else None,
            ProviderType.OPENAI: config.openai.dict() if config.openai else None,
            ProviderType.MCP: config.mcp.dict() if config.mcp else None,
        }
        
        provider_config = provider_configs.get(config.provider)
        if not provider_config:
            raise ValueError(f"No configuration found for provider: {config.provider}")
        
        return create_provider(config.provider.value, provider_config)

    def execute_command(self, command: str) -> str:
        """Execute a command and return the response."""
        with self.lock:
            prompt = f"Pretend to be a Bash shell on an Ubuntu Linux system. Do not respond with anything other than what the user would see in the terminal after running this command: {command}"
            return self.provider.generate_response(prompt)

def main():
    parser = argparse.ArgumentParser(description="AI Honeypot Bash Shell")
    parser.add_argument("--endpoint", type=str, help="Endpoint for the LLaMA model API (legacy)")
    parser.add_argument("--provider", type=str, choices=["llama", "openai", "mcp"], 
                       help="AI provider to use")
    parser.add_argument("--tcp", action="store_true",
                       help="Run as TCP server instead of interactive shell")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                       help="Host to bind to in TCP mode (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=2222,
                       help="Port to listen on in TCP mode (default: 2222)")
    args = parser.parse_args()

    # If TCP mode is requested, start the TCP server
    if args.tcp:
        from tcp_server import SSHTCPServer
        server = SSHTCPServer(
            host=args.host,
            port=args.port,
            endpoint=args.endpoint,
            provider=args.provider
        )
        return server.start()

    # Otherwise, run in interactive mode
    try:
        bash_shell = BashShell(args.endpoint, args.provider)
        
        print("AI Honeypot Bash Shell - Type 'exit' to quit")
        print("Provider:", bash_shell.provider.__class__.__name__)
        
        while True:
            command = input("bash$: ")
            if not command.strip():
                continue
            if command.lower() in ['exit', 'quit']:
                break
                
            try:
                response = bash_shell.execute_command(command)
                print(response)
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Failed to initialize: {e}")
        return 1

if __name__ == "__main__":
    main()
