import socket
import sys
from threading import Thread

address = ('0.0.0.0', 6666)

def send_broadcast(clients, message, username_sender):
    for username in clients.keys():
        if username == username_sender:
            continue
        send_message(clients[username][0], message)

def send_message(sock_destination, message):
    sock_destination.send(message.encode('utf-8'))

def serve_client(clients, sock_client, addr_client, username):
    while True:
        data = sock_client.recv(65535)
        if len(data) == 0:
            break

        destination, message = data.decode('utf-8').split('|', 1)
        formatted_message = f'<{username}>: {message}'

        if destination == '_bcast':
            send_broadcast(clients, formatted_message, username)
        else:
            send_message(clients[destination][0], formatted_message)
            
        
        message_log = f'[{username} -> {destination}] {message}'
        print(message_log)
    pass

def main():
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.bind(address)
    sock_server.listen(10)

    clients = {}

    while True:
        sock_client, addr_client = sock_server.accept()
        username = sock_client.recv(65535).decode('utf-8')
        print(f'{username} connected from {addr_client}')

        thread = Thread(target=serve_client, args=(clients, sock_client, addr_client, username))
        thread.start()

        clients[username] = (sock_client, addr_client, thread)

if __name__ == '__main__':
    main()
