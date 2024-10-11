import socket
import threading
import json
import signal
import sys
from mitmproxy import http

clients = []
server_socket = None

def handle_client(client_socket):
    try:
        while True:
            message = client_socket.recv(1024)
            if not message:
                break
    except:
        pass
    finally:
        client_socket.close()

def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 9999))
    server_socket.listen(5)
    print("[*] Server started on port 9999")

    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"[*] Accepted connection from {addr}")
            clients.append(client_socket)
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()
        except OSError:
            break

def broadcast_data(data):
    for client in clients:
        try:
            client.sendall(data.encode())
        except:
            clients.remove(client)

def signal_handler(sig, frame):
    print("\n[*] Shutting down the server...")
    if server_socket:
        server_socket.close()
    for client in clients:
        client.close()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

def response(flow: http.HTTPFlow):
    if "https://xyks.yuanfudao.com/leo-game-pk/android/math/pk/match" in flow.request.url:
        json_data = json.loads(flow.response.text)
        questionlist = json_data["examVO"]["questions"]
        answers = [ans["answer"] for ans in questionlist]
        print(answers)
        answers_json = json.dumps(answers)
        broadcast_data(answers_json)
        
        
        
        
        
        # mitmdump -s catchPExec.py