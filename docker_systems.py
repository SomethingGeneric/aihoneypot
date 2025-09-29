"""Docker system management for AI Honeypot.

This module provides the foundation for future Docker-based system simulation.
It can be extended to run honeypots in isolated containers with different
operating systems and configurations.
"""

import docker
import json
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod

class DockerSystemManager:
    """Manages Docker containers for system simulation."""
    
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            raise Exception(f"Failed to connect to Docker: {e}")
    
    def create_honeypot_container(self, 
                                image: str = "ubuntu:22.04",
                                name: str = "honeypot",
                                environment: Optional[Dict[str, str]] = None) -> str:
        """Create a new honeypot container."""
        try:
            container = self.client.containers.run(
                image=image,
                name=name,
                environment=environment or {},
                detach=True,
                tty=True,
                stdin_open=True,
                remove=False
            )
            return container.id
        except Exception as e:
            raise Exception(f"Failed to create container: {e}")
    
    def execute_in_container(self, container_id: str, command: str) -> Dict[str, Any]:
        """Execute a command in a Docker container."""
        try:
            container = self.client.containers.get(container_id)
            result = container.exec_run(command, stdout=True, stderr=True)
            
            return {
                "exit_code": result.exit_code,
                "stdout": result.output.decode('utf-8', errors='ignore'),
                "stderr": ""  # Docker API combines stdout/stderr
            }
        except Exception as e:
            raise Exception(f"Failed to execute command in container: {e}")
    
    def list_containers(self) -> List[Dict[str, Any]]:
        """List all honeypot containers."""
        try:
            containers = self.client.containers.list(all=True)
            return [
                {
                    "id": c.id[:12],
                    "name": c.name,
                    "status": c.status,
                    "image": c.image.tags[0] if c.image.tags else "unknown"
                }
                for c in containers
                if c.name.startswith("honeypot")
            ]
        except Exception as e:
            raise Exception(f"Failed to list containers: {e}")
    
    def remove_container(self, container_id: str, force: bool = True):
        """Remove a honeypot container."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
        except Exception as e:
            raise Exception(f"Failed to remove container: {e}")

class DockerBashShell:
    """Docker-based bash shell simulation.
    
    This class provides a foundation for running honeypot shells in Docker
    containers, offering better isolation and more realistic system behavior.
    """
    
    def __init__(self, 
                 image: str = "ubuntu:22.04",
                 ai_provider: Optional[Any] = None):
        self.docker_manager = DockerSystemManager()
        self.ai_provider = ai_provider
        self.container_id = None
        self.image = image
        
    def start(self) -> str:
        """Start a new Docker container for the shell."""
        if self.container_id:
            raise Exception("Shell already started")
            
        self.container_id = self.docker_manager.create_honeypot_container(
            image=self.image,
            name=f"honeypot-shell-{hash(self) % 10000}"
        )
        return self.container_id
    
    def execute_command(self, command: str, use_ai: bool = True) -> str:
        """Execute a command either in Docker or via AI simulation."""
        if not self.container_id:
            raise Exception("Shell not started. Call start() first.")
        
        if use_ai and self.ai_provider:
            # Use AI to simulate the command
            prompt = f"Pretend to be a Bash shell on an Ubuntu Linux system in a Docker container. Simulate the output for: {command}"
            return self.ai_provider.generate_response(prompt)
        else:
            # Execute in actual Docker container
            result = self.docker_manager.execute_in_container(self.container_id, command)
            return result["stdout"]
    
    def stop(self):
        """Stop and remove the Docker container."""
        if self.container_id:
            self.docker_manager.remove_container(self.container_id)
            self.container_id = None

    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop()

# Example configuration for different system types
SYSTEM_CONFIGS = {
    "ubuntu": {
        "image": "ubuntu:22.04",
        "description": "Ubuntu 22.04 LTS system"
    },
    "centos": {
        "image": "centos:8",
        "description": "CentOS 8 system"
    },
    "alpine": {
        "image": "alpine:latest",
        "description": "Alpine Linux system (minimal)"
    },
    "debian": {
        "image": "debian:bullseye",
        "description": "Debian 11 (Bullseye) system"
    }
}