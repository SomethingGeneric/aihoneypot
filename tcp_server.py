"""TCP server for AI Honeypot with SSH-like functionality."""

import socket
import threading
import signal
import sys
import time
from typing import Optional
from bash import BashShell


class SSHTCPServer:
    """TCP server that mimics SSH server behavior for honeypot purposes."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2222, 
                 endpoint: Optional[str] = None, provider: Optional[str] = None):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.provider = provider
        self.server_socket = None
        self.running = False
        self.sessions = []
        
    def start(self):
        """Start the TCP server."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"AI Honeypot SSH Server started on {self.host}:{self.port}")
            print("Press Ctrl+C to stop")
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            while self.running:
                try:
                    self.server_socket.settimeout(1.0)
                    try:
                        client_socket, address = self.server_socket.accept()
                        print(f"New connection from {address[0]}:{address[1]}")
                        
                        # Handle each client in a separate thread
                        client_thread = threading.Thread(
                            target=self._handle_client,
                            args=(client_socket, address),
                            daemon=True
                        )
                        client_thread.start()
                        self.sessions.append(client_thread)
                    except socket.timeout:
                        continue
                except Exception as e:
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        
        except Exception as e:
            print(f"Failed to start server: {e}")
            return 1
        finally:
            self.stop()
            
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print("\nShutting down server...")
        self.running = False
        
    def stop(self):
        """Stop the server and close all connections."""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("Server stopped")
        
    def _handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle a client connection."""
        try:
            # Send SSH banner to mimic OpenSSH
            banner = b"SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.1\r\n"
            client_socket.send(banner)
            
            # Give client time to respond
            time.sleep(0.1)
            
            # Try to read client banner
            client_socket.settimeout(5.0)
            try:
                client_banner = client_socket.recv(1024)
            except socket.timeout:
                client_banner = b""
            
            # Simple fake SSH auth - just send prompts and accept anything
            client_socket.send(b"login: ")
            try:
                username = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()
            except:
                username = "anonymous"
                
            if not username:
                client_socket.close()
                return
                
            client_socket.send(b"Password: ")
            try:
                password = client_socket.recv(1024).decode('utf-8', errors='ignore').strip()
            except:
                password = ""
            
            # Log the authentication attempt
            print(f"[{address[0]}] Login attempt - User: {username}, Pass: {password}")
            
            # Always "authenticate successfully"
            welcome_msg = f"Welcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-58-generic x86_64)\r\n\r\n"
            welcome_msg += "Last login: " + time.strftime("%a %b %d %H:%M:%S %Y") + f" from {address[0]}\r\n"
            client_socket.send(welcome_msg.encode('utf-8'))
            
            # Initialize the AI shell for this session
            bash_shell = BashShell(self.endpoint, self.provider)
            
            # Main shell loop
            while self.running:
                try:
                    # Send prompt
                    client_socket.send(b"bash$: ")
                    
                    # Receive command
                    client_socket.settimeout(300.0)  # 5 minute timeout
                    data = client_socket.recv(4096)
                    
                    if not data:
                        break
                        
                    command = data.decode('utf-8', errors='ignore').strip()
                    
                    if not command:
                        continue
                        
                    # Log command
                    print(f"[{address[0]}:{username}] Command: {command}")
                    
                    # Handle exit commands
                    if command.lower() in ['exit', 'quit', 'logout']:
                        client_socket.send(b"logout\r\n")
                        break
                    
                    # Execute command via AI
                    try:
                        response = bash_shell.execute_command(command)
                        # Ensure proper line endings for network transmission
                        response = response.replace('\n', '\r\n')
                        client_socket.send((response + '\r\n').encode('utf-8'))
                    except Exception as e:
                        error_msg = f"Error: {str(e)}\r\n"
                        client_socket.send(error_msg.encode('utf-8'))
                        
                except socket.timeout:
                    print(f"[{address[0]}] Session timeout")
                    break
                except Exception as e:
                    print(f"[{address[0]}] Error in session: {e}")
                    break
                    
        except Exception as e:
            print(f"[{address[0]}] Connection error: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass
            print(f"[{address[0]}] Connection closed")


def main():
    """Main entry point for TCP server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Honeypot SSH-like TCP Server")
    parser.add_argument("--host", type=str, default="0.0.0.0",
                       help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=2222,
                       help="Port to listen on (default: 2222)")
    parser.add_argument("--endpoint", type=str, 
                       help="Endpoint for the LLaMA model API (legacy)")
    parser.add_argument("--provider", type=str, choices=["llama", "openai", "mcp"],
                       help="AI provider to use")
    args = parser.parse_args()
    
    server = SSHTCPServer(
        host=args.host,
        port=args.port,
        endpoint=args.endpoint,
        provider=args.provider
    )
    
    return server.start()


if __name__ == "__main__":
    sys.exit(main() or 0)
