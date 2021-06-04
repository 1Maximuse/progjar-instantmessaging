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

def add_friend(friends, sock_sender, sock_recipient, sender, recipient):
    if (sender, recipient) in friends and (recipient, sender) in friends:
        sock_sender.send(f'_alreadyfriends|{recipient}'.encode('utf-8'))
    elif (sender, recipient) in friends:
        sock_sender.send(f'_requestexists|{recipient}'.encode('utf-8'))
    else:
        friends.add((sender, recipient))
        sock_sender.send(f'_requestcreated|{recipient}'.encode('utf-8'))
        sock_recipient.send(f'_request|{sender}'.encode('utf-8'))

def accept_friend(friends, sock_destination, requester, accepter):
    friends.add((accepter, requester))
    sock_destination.send(f'_requestaccepted|{accepter}'.encode('utf-8'))

def serve_client(clients, friends, sock_client, addr_client, username):
    while True:
        data = sock_client.recv(65535)
        if len(data) == 0:
            break

        destination, message = data.decode('utf-8').split('|', 1)
        formatted_message = f'<{username}>: {message}'

        message_log = ''

        if destination == '_bcast':
            send_broadcast(clients, friends, formatted_message, username)
            message_log = f'[{username} -> {destination}] {message}'
        elif destination == '_req':
            add_friend(friends, sock_client, clients[message][0], username, message)
            message_log = f'[Friend request: {username} -> {message}]'
        elif destination == '_acc':
            accept_friend(friends, clients[message][0], message, username)
            message_log = f'[Friend request accepted: {username} -> {message}]'
        else:
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
    