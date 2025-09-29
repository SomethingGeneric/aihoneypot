"""Configuration management for AI Honeypot providers."""

import os
from enum import Enum
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ProviderType(str, Enum):
    LLAMA = "llama"
    OPENAI = "openai"
    MCP = "mcp"

class LlamaConfig(BaseModel):
    endpoint: str
    model: str = "llama3.2"

class OpenAIConfig(BaseModel):
    api_key: str
    model: str = "gpt-3.5-turbo"
    base_url: Optional[str] = None

class MCPConfig(BaseModel):
    server_path: str
    server_args: list[str] = []
    timeout: int = 30

class Config(BaseModel):
    provider: ProviderType = ProviderType.LLAMA
    llama: Optional[LlamaConfig] = None
    openai: Optional[OpenAIConfig] = None
    mcp: Optional[MCPConfig] = None

def load_config() -> Config:
    """Load configuration from environment variables or use defaults."""
    provider = ProviderType(os.getenv("AI_PROVIDER", "llama"))
    
    config_data = {"provider": provider}
    
    # Load LLaMA config
    if provider == ProviderType.LLAMA or os.getenv("LLAMA_ENDPOINT"):
        config_data["llama"] = LlamaConfig(
            endpoint=os.getenv("LLAMA_ENDPOINT", "http://localhost:11434"),
            model=os.getenv("LLAMA_MODEL", "llama3.2")
        )
    
    # Load OpenAI config
    if provider == ProviderType.OPENAI or os.getenv("OPENAI_API_KEY"):
        config_data["openai"] = OpenAIConfig(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            base_url=os.getenv("OPENAI_BASE_URL")
        )
    
    # Load MCP config
    if provider == ProviderType.MCP or os.getenv("MCP_SERVER_PATH"):
        config_data["mcp"] = MCPConfig(
            server_path=os.getenv("MCP_SERVER_PATH", ""),
            server_args=os.getenv("MCP_SERVER_ARGS", "").split() if os.getenv("MCP_SERVER_ARGS") else [],
            timeout=int(os.getenv("MCP_TIMEOUT", "30"))
        )
    
    return Config(**config_data)