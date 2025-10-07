"""TCP server for AI Honeypot with SSH functionality."""

import socket
import threading
import signal
import sys
import time
import paramiko
import io
from typing import Optional
from bash import BashShell


class HoneypotSSHServer(paramiko.ServerInterface):
    """SSH server interface for honeypot that accepts all authentication."""
    
    def __init__(self, address: str):
        self.address = address
        self.username = None
        self.password = None
        self.exec_command = None
        self.event = threading.Event()
        
    def check_auth_password(self, username: str, password: str) -> int:
        """Accept any password and log the attempt."""
        self.username = username
        self.password = password
        print(f"[{self.address}] Login attempt - User: {username}, Pass: {password}")
        return paramiko.AUTH_SUCCESSFUL
    
    def check_auth_publickey(self, username: str, key: paramiko.PKey) -> int:
        """Accept any public key and log the attempt."""
        self.username = username
        print(f"[{self.address}] Public key auth attempt - User: {username}")
        return paramiko.AUTH_SUCCESSFUL
    
    def get_allowed_auths(self, username: str) -> str:
        """Allow both password and public key authentication."""
        return "password,publickey"
    
    def check_channel_request(self, kind: str, chanid: int) -> int:
        """Accept session channel requests."""
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_channel_shell_request(self, channel: paramiko.Channel) -> bool:
        """Accept shell requests."""
        self.event.set()
        return True
    
    def check_channel_pty_request(self, channel: paramiko.Channel, term: bytes,
                                   width: int, height: int, pixelwidth: int,
                                   pixelheight: int, modes: bytes) -> bool:
        """Accept PTY requests."""
        return True
    
    def check_channel_exec_request(self, channel: paramiko.Channel, command: bytes) -> bool:
        """Accept exec requests."""
        self.exec_command = command.decode('utf-8', errors='ignore')
        self.event.set()
        return True


class SSHTCPServer:
    """TCP server that implements SSH protocol for honeypot purposes."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 2222, 
                 endpoint: Optional[str] = None, provider: Optional[str] = None):
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.provider = provider
        self.server_socket = None
        self.running = False
        self.sessions = []
        self.host_key = None
        self._generate_host_key()
    
    def _generate_host_key(self):
        """Generate an RSA host key for the SSH server."""
        try:
            self.host_key = paramiko.RSAKey.generate(2048)
        except Exception as e:
            print(f"Warning: Could not generate RSA key: {e}")
            print("Server will not be able to accept SSH connections")
        
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
        """Handle a client connection with SSH protocol."""
        transport = None
        try:
            # Create SSH transport
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(self.host_key)
            
            # Set up the SSH server interface
            server = HoneypotSSHServer(address[0])
            
            try:
                transport.start_server(server=server)
            except paramiko.SSHException as e:
                print(f"[{address[0]}] SSH negotiation failed: {e}")
                return
            
            # Wait for authentication
            channel = transport.accept(20)
            if channel is None:
                print(f"[{address[0]}] No channel opened")
                return
            
            # Wait for shell or exec request
            server.event.wait(10)
            if not server.event.is_set():
                print(f"[{address[0]}] Client never asked for a shell or exec")
                channel.close()
                return
            
            username = server.username or "unknown"
            
            # Initialize the AI shell for this session
            bash_shell = BashShell(self.endpoint, self.provider)
            
            # Check if this is an exec command (single command execution)
            if server.exec_command:
                # Log and execute the command
                command = server.exec_command
                print(f"[{address[0]}:{username}] Exec command: {command}")
                
                try:
                    response = bash_shell.execute_command(command)
                    channel.send(response)
                    if not response.endswith('\n'):
                        channel.send('\n')
                except Exception as e:
                    error_msg = f"Error: {str(e)}\n"
                    channel.send(error_msg)
                
                channel.send_exit_status(0)
                channel.close()
                return
            
            # This is an interactive shell session
            # Send welcome message
            welcome_msg = f"Welcome to Ubuntu 22.04.1 LTS (GNU/Linux 5.15.0-58-generic x86_64)\r\n\r\n"
            welcome_msg += "Last login: " + time.strftime("%a %b %d %H:%M:%S %Y") + f" from {address[0]}\r\n"
            channel.send(welcome_msg)
            
            # Main shell loop
            channel.settimeout(300.0)  # 5 minute timeout
            while self.running:
                try:
                    # Send prompt
                    channel.send("bash$: ")
                    
                    # Receive command (read until newline)
                    command_buffer = b""
                    while True:
                        char = channel.recv(1)
                        if not char:
                            break
                        if char in (b'\n', b'\r'):
                            break
                        # Handle backspace/delete
                        if char in (b'\x7f', b'\x08'):
                            if command_buffer:
                                command_buffer = command_buffer[:-1]
                                # Move cursor back, overwrite with space, move back again
                                channel.send(b'\x08 \x08')
                        else:
                            command_buffer += char
                            # Echo the character back to the client
                            channel.send(char)
                    
                    if not command_buffer:
                        break
                        
                    command = command_buffer.decode('utf-8', errors='ignore').strip()
                    
                    if not command:
                        channel.send("\r\n")
                        continue
                        
                    # Log command
                    print(f"[{address[0]}:{username}] Command: {command}")
                    
                    # Handle exit commands
                    if command.lower() in ['exit', 'quit', 'logout']:
                        channel.send("\r\n")
                        channel.send("logout\r\n")
                        break
                    
                    # Execute command via AI
                    try:
                        # Send newline after command input before showing output
                        channel.send("\r\n")
                        response = bash_shell.execute_command(command)
                        # Ensure proper line endings for network transmission
                        response = response.replace('\n', '\r\n')
                        channel.send(response + '\r\n')
                    except Exception as e:
                        error_msg = f"Error: {str(e)}\r\n"
                        channel.send(error_msg)
                        
                except socket.timeout:
                    print(f"[{address[0]}] Session timeout")
                    break
                except Exception as e:
                    print(f"[{address[0]}] Error in session: {e}")
                    break
            
            channel.close()
                    
        except Exception as e:
            print(f"[{address[0]}] Connection error: {e}")
        finally:
            if transport:
                try:
                    transport.close()
                except:
                    pass
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
