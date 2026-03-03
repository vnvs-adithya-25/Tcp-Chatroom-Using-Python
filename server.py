import socket
import threading

# Server Configuration
host = '127.0.0.1'
port = 55555

# Create Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow address reuse (Fix for WinError 10048)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((host, port))
server.listen()

print("Server started...")

# Lists For Clients and Nicknames
clients = []
nicknames = []

# Thread lock for safety
lock = threading.Lock()

# Broadcast message to all clients
def broadcast(message):
    with lock:
        for client in clients:
            try:
                client.send(message)
            except Exception as e:
                print("Broadcast Error:", e)

# Handle messages from a client
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                remove_client(client)
                break
            broadcast(message)
        except Exception as e:
            print("Handle Error:", e)
            remove_client(client)
            break

# Remove client helper function
def remove_client(client):
    with lock:
        if client in clients:
            index = clients.index(client)
            nickname = nicknames[index]

            clients.remove(client)
            nicknames.remove(nickname)
            client.close()

            print(f"{nickname} disconnected")
            broadcast(f"{nickname} left the chat!".encode('utf-8'))

# Accept new clients
def receive():
    print("Server is Listening...")
    while True:
        try:
            client, address = server.accept()
            print(f"Connected with {address}")

            client.send("NICK".encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')

            with lock:
                nicknames.append(nickname)
                clients.append(client)

            print(f"Nickname is {nickname}")
            broadcast(f"{nickname} joined the chat!".encode('utf-8'))
            client.send("Connected to server!".encode('utf-8'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except Exception as e:
            print("Server Error:", e)
            break

# Run Server
try:
    receive()
except KeyboardInterrupt:
    print("\nServer shutting down...")
finally:
    server.close()