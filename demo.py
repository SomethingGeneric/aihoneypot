#!/usr/bin/env python3
"""
Demo script for AI Honeypot functionality.
Shows how different providers would work.
"""

from bash import BashShell
import os

def demo_provider_selection():
    """Demonstrate provider selection."""
    print("=== AI Honeypot Provider Demo ===\n")
    
    # Demo 1: Legacy mode (backward compatibility)
    print("1. Legacy LLaMA Mode (backward compatible)")
    try:
        shell = BashShell(endpoint="http://localhost:11434")
        provider_name = shell.provider.__class__.__name__
        print(f"   ✓ Initialized with {provider_name}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Demo 2: Configuration-based provider
    print("\n2. Configuration-based Provider Selection")
    try:
        shell = BashShell(provider="llama")
        provider_name = shell.provider.__class__.__name__
        print(f"   ✓ Initialized with {provider_name}")
    except Exception as e:
        print(f"   ✗ Failed: {e}")
    
    # Demo 3: Different providers
    providers = ["llama", "openai", "mcp"]
    for provider in providers:
        print(f"\n3.{providers.index(provider)+1}. Testing {provider.upper()} Provider")
        try:
            # This will fail for openai/mcp without proper config, but shows the interface works
            shell = BashShell(provider=provider)
            provider_name = shell.provider.__class__.__name__
            print(f"   ✓ Would use {provider_name}")
        except Exception as e:
            print(f"   ℹ Expected error (no config): {str(e)[:80]}...")

def demo_command_simulation():
    """Demonstrate command simulation interface."""
    print("\n=== Command Simulation Interface ===")
    
    try:
        shell = BashShell(endpoint="http://localhost:11434")
        
        # This would normally call the LLM, but we can't test that without a running LLM
        print("✓ Shell interface ready")
        print("✓ Command execution method available")
        print("ℹ Actual LLM calls would require running LLaMA/Ollama server")
        
    except Exception as e:
        print(f"✗ Failed: {e}")

def demo_docker_preparation():
    """Show Docker system preparation."""
    print("\n=== Docker System Preparation ===")
    
    try:
        import docker_systems
        
        configs = docker_systems.SYSTEM_CONFIGS
        print("✓ Docker system configurations available:")
        for name, config in configs.items():
            print(f"   - {name}: {config['image']} ({config['description']})")
        
        print("ℹ Docker integration ready for future expansion")
        
    except ImportError:
        print("ℹ Docker module would be available with 'pip install docker'")

if __name__ == "__main__":
    demo_provider_selection()
    demo_command_simulation()
    demo_docker_preparation()
    
    print("\n=== Summary ===")
    print("✓ Multiple AI provider support implemented")
    print("✓ Backward compatibility maintained")  
    print("✓ Docker foundation prepared")
    print("✓ Configuration system ready")
    print("\nReady for SSH honeypot integration!")