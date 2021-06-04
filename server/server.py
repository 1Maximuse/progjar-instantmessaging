import socket
import sys
from threading import Thread

address = ('0.0.0.0', 6666)

def send_broadcast(clients, friends, formatted_message, username_sender):
    for username in clients.keys():
        if username == username_sender:
            continue
        if (username_sender, username) in friends and (username, username_sender) in friends:
            clients[username][0].send(formatted_message.encode('utf-8'))

def send_message(friends, sock_sender, sock_destination, username, destination, formatted_message):
    if (username, destination) in friends and (destination, username) in friends:
        sock_destination.send(formatted_message.encode('utf-8'))
    else:
        sock_sender.send(f'_notfriends|{destination}'.encode('utf-8'))

def send_file(friends, sock_sender, sock_destination, username, destination, name, size, filedata):
    if (username, destination) in friends and (destination, username) in friends:
        message = f'_acceptfile|{username}|{name}|{size}|'.encode('utf-8')
        message += filedata
        sock_destination.sendall(message)
    else:
        sock_sender.send(f'_notfriends|{destination}'.encode('utf-8'))

def add_friend(friends, sock_sender, sock_recipient, sender, recipient):
    if (sender, recipient) in friends and (recipient, sender) in friends:
        sock_sender.send(f'_alreadyfriends|{recipient}'.encode('utf-8'))
    elif (sender, recipient) in friends:
        sock_sender.send(f'_requestexists|{recipient}'.encode('utf-8'))
    else:
        friends.add((sender, recipient))
        sock_sender.send(f'_requestcreated|{recipient}'.encode('utf-8'))
        sock_recipient.send(f'_request|{sender}'.encode('utf-8'))

def accept_friend(friends, sock_sender, sock_destination, requester, accepter):
    friends.add((accepter, requester))
    sock_destination.send(f'_requestaccepted|{accepter}'.encode('utf-8'))
    sock_sender.send(f'_requestsentaccept|{requester}'.encode('utf-8'))

def serve_client(clients, friends, sock_client, addr_client, username):
    while True:
        data = sock_client.recv(65535)
        if len(data) == 0:
            break

        message_log = ''

        destination, message = data.split(b'|', 1)
        destination = destination.decode('utf-8')
        if destination != '_sendfile':
            message = message.decode('utf-8')

        if destination == '_bcast':
            formatted_message = f'<{username}>: {message}'
            send_broadcast(clients, friends, formatted_message, username)
            message_log = f'[{username} -> {destination}] {message}'
        elif destination == '_req':
            add_friend(friends, sock_client, clients[message][0], username, message)
            message_log = f'[Friend request: {username} -> {message}]'
        elif destination == '_acc':
            accept_friend(friends, sock_client, clients[message][0], message, username)
            message_log = f'[Friend request accepted: {username} -> {message}]'
        elif destination == '_sendfile':
            recipient, name, size, filedata = message.split(b'|', 3)
            recipient = recipient.decode('utf-8')
            name = name.decode('utf-8')
            size = int(size.decode('utf-8'))

            while len(filedata) < size:
                if size - len(filedata) > 65536:
                    filedata += sock_client.recv(65536)
                else:
                    filedata += sock_client.recv(size - len(filedata))
                    break
            
            send_file(friends, sock_client, clients[recipient][0], username, recipient, name, size, filedata)
            message_log = f'[{username} -> {recipient}] Sent file {name} of size {size} bytes'
        else:
            formatted_message = f'<{username}>: {message}'
            send_message(friends, sock_client, clients[destination][0], username, destination, formatted_message)
            message_log = f'[{username} -> {destination}] {message}'
        
        print(message_log)

def main():
    sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_server.bind(address)
    sock_server.listen(10)

    clients = {}
    friends = set()

    while True:
        sock_client, addr_client = sock_server.accept()
        username = sock_client.recv(65535).decode('utf-8')
        print(f'{username} connected from {addr_client}')

        thread = Thread(target=serve_client, args=(clients, friends, sock_client, addr_client, username))
        thread.start()

        clients[username] = (sock_client, addr_client, thread)

if __name__ == '__main__':
    main()