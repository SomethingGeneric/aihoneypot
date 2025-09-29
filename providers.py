"""Provider implementations for different LLM services."""

import requests
import asyncio
import subprocess
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from config import LlamaConfig, OpenAIConfig, MCPConfig

class BaseProvider(ABC):
    """Base class for all LLM providers."""
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a response using the provider's LLM."""
        pass

class LlamaProvider(BaseProvider):
    """Provider for LLaMA models via Ollama API."""
    
    def __init__(self, config: LlamaConfig):
        self.config = config
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using LLaMA model."""
        url = f"{self.config.endpoint}/api/generate"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.config.model,
            "stream": False,
            "prompt": prompt
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            raise Exception(f"LLaMA API failed with status code {response.status_code}")

class OpenAIProvider(BaseProvider):
    """Provider for OpenAI models."""
    
    def __init__(self, config: OpenAIConfig):
        self.config = config
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=config.api_key,
                base_url=config.base_url
            )
        except ImportError:
            raise ImportError("OpenAI package not installed. Install with: pip install openai")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using OpenAI model."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API failed: {str(e)}")

class MCPProvider(BaseProvider):
    """Provider for Model Context Protocol (MCP) servers."""
    
    def __init__(self, config: MCPConfig):
        self.config = config
        self.server_process = None
        self._start_server()
    
    def _start_server(self):
        """Start the MCP server process."""
        try:
            self.server_process = subprocess.Popen(
                [self.config.server_path] + self.config.server_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        except Exception as e:
            raise Exception(f"Failed to start MCP server: {str(e)}")
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using MCP server."""
        if not self.server_process or self.server_process.poll() is not None:
            raise Exception("MCP server is not running")
        
        try:
            # Send request to MCP server
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "generate",
                "params": {"prompt": prompt}
            }
            
            self.server_process.stdin.write(json.dumps(request) + "\n")
            self.server_process.stdin.flush()
            
            # Read response
            response_line = self.server_process.stdout.readline()
            if not response_line:
                raise Exception("No response from MCP server")
            
            response = json.loads(response_line.strip())
            if "error" in response:
                raise Exception(f"MCP server error: {response['error']}")
            
            return response.get("result", {}).get("content", "")
        
        except Exception as e:
            raise Exception(f"MCP communication failed: {str(e)}")
    
    def __del__(self):
        """Clean up the MCP server process."""
        if self.server_process and self.server_process.poll() is None:
            self.server_process.terminate()
            self.server_process.wait()

def create_provider(provider_type: str, config: Dict[str, Any]) -> BaseProvider:
    """Factory function to create providers."""
    if provider_type == "llama":
        return LlamaProvider(LlamaConfig(**config))
    elif provider_type == "openai":
        return OpenAIProvider(OpenAIConfig(**config))
    elif provider_type == "mcp":
        return MCPProvider(MCPConfig(**config))
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")