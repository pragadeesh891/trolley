"""
Script to start a public tunnel to the Smart Shopping Trolley application
using ngrok for remote access.
"""

from pyngrok import ngrok
import subprocess
import threading
import time
import sys

def start_server():
    """Start the FastAPI server"""
    try:
        # Start the FastAPI server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        return process
    except Exception as e:
        print(f"Error starting server: {e}")
        return None

def start_tunnel():
    """Start ngrok tunnel"""
    try:
        # Start ngrok tunnel to port 8000
        public_url = ngrok.connect(8000)
        print(f"==============================================")
        print(f"Public URL: {public_url}")
        print(f"Share this URL with your friends to access the application")
        print(f"==============================================")
        return public_url
    except Exception as e:
        print(f"Error starting tunnel: {e}")
        return None

def main():
    print("Starting Smart Shopping Trolley with public access...")
    
    # Start the server in a separate thread
    server_process = start_server()
    if not server_process:
        print("Failed to start server")
        return
    
    # Wait a moment for server to start
    time.sleep(3)
    
    # Start the tunnel
    tunnel_url = start_tunnel()
    if not tunnel_url:
        print("Failed to start tunnel")
        server_process.terminate()
        return
    
    print("Server and tunnel are running. Press Ctrl+C to stop.")
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        ngrok.kill()
        server_process.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()