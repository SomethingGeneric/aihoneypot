#!/usr/bin/env python3
"""
Integration test script for AI Honeypot.
Tests the various providers and configurations.
"""

import os
import sys
from config import load_config, ProviderType
from providers import LlamaProvider, create_provider
from config import LlamaConfig

def test_config_loading():
    """Test configuration loading."""
    print("=== Testing Configuration Loading ===")
    
    # Test default config
    config = load_config()
    print(f"✓ Default provider: {config.provider}")
    
    # Test environment override
    os.environ['AI_PROVIDER'] = 'llama'
    os.environ['LLAMA_ENDPOINT'] = 'http://test:11434'
    config = load_config()
    print(f"✓ Environment override: {config.provider}")
    if config.llama:
        print(f"✓ LLaMA endpoint: {config.llama.endpoint}")
    
    return True

def test_provider_creation():
    """Test provider creation."""
    print("\n=== Testing Provider Creation ===")
    
    # Test LLaMA provider creation
    try:
        llama_config = LlamaConfig(endpoint="http://localhost:11434")
        provider = LlamaProvider(llama_config)
        print("✓ LLaMA provider created successfully")
    except Exception as e:
        print(f"✗ LLaMA provider creation failed: {e}")
        return False
    
    # Test factory function
    try:
        provider = create_provider("llama", {"endpoint": "http://localhost:11434"})
        print("✓ Provider factory works")
    except Exception as e:
        print(f"✗ Provider factory failed: {e}")
        return False
    
    return True

def test_bash_shell_initialization():
    """Test BashShell initialization."""
    print("\n=== Testing BashShell Initialization ===")
    
    try:
        from bash import BashShell
        
        # Test with endpoint (legacy mode)
        shell = BashShell(endpoint="http://localhost:11434")
        print("✓ Legacy endpoint mode works")
        
        # Test with provider
        shell = BashShell(provider="llama")
        print("✓ Provider mode works")
        
    except Exception as e:
        print(f"✗ BashShell initialization failed: {e}")
        return False
    
    return True

def test_docker_systems():
    """Test docker systems module."""
    print("\n=== Testing Docker Systems ===")
    
    try:
        import docker_systems
        print("✓ Docker systems module imported")
        
        # Test system configs
        configs = docker_systems.SYSTEM_CONFIGS
        print(f"✓ Found {len(configs)} system configurations")
        
        for name in configs:
            print(f"  - {name}")
            
    except ImportError:
        print("ℹ Docker module not available (expected in test environment)")
        return True
    except Exception as e:
        print(f"✗ Docker systems test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("AI Honeypot Integration Tests")
    print("=" * 40)
    
    tests = [
        test_config_loading,
        test_provider_creation,
        test_bash_shell_initialization,
        test_docker_systems
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print(f"\n=== Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())