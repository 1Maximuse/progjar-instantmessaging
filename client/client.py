import socket
import sys
from threading import Lock, Thread

remote_address = ('127.0.0.1', 6666)

lock = Lock()

position = 0

def receive_message(sock_client):
    while True:
        data = sock_client.recv(65535)
        if len(data) == 0:
            break
        status = data.decode('utf-8').split("|", 1)[0]
        
        if status == "_request":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rReceived friend request from {username}, enter _acc {username} to accept.\n----------\n>> ', end='')
        elif status == "_requestcreated":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rFriend request to {username} sent.\n----------\n>> ', end='')
        elif status == "_requestexists":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rYou have already sent {username} a friend request.\n----------\n>> ', end='')
        elif status == "_requestaccepted":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rYour friend request has been accepted by {username}.\n----------\n>> ', end='')
        elif status == "_alreadyfriends":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rYou already have {username} in your friend list.\n----------\n>> ', end='')
        elif status == "_notfriends":
            username = data.decode('utf-8').split("|", 1)[1]
            print(f'\rYou are not friend with {username} yet.\n----------\n>> ', end='')
        else:
            print(data.decode('utf-8'))

def main():
    username = input('Set username: ').strip().lstrip('_').replace('|', '')
    print(f'Username set: {username}')

    sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_client.connect(remote_address)

    sock_client.send(username.encode('utf-8'))

    thread_receive = Thread(target=receive_message, args=(sock_client,))
    thread_receive.start()

    while True:
        dest = input('----------\nAvailable commands:\n_bcast <message>\tBroadcast a message\n<recipient> <message>\tSend a message to recipient\n_req <username>\tSend a friend request to username\n_acc <username>\tAccept a friend request from username\n_quit\tExit the app\n----------\n>> ')
        command = dest.split(" ", 1)
        if command[0] == '_quit':
            sock_client.close()
            break
        else:
            sock_client.send(f'{command[0]}|{command[1]}'.encode('utf-8'))

if __name__ == '__main__':
    main()