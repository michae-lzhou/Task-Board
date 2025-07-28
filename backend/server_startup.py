################################################################################
# server_startup.py
# Purpose:  Simply starts up the backend with WebSocket
################################################################################

# Libraries
import uvicorn

# Local files
from main import socket_app

if __name__ == "__main__":
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
