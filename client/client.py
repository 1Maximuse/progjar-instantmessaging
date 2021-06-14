import os
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
        status, message = data.split(b"|", 1)
        status = status.decode('utf-8')
        if status != '_acceptfile':
            message = message.decode('utf-8')
        
        if status == "_request":
            print(f'\rReceived friend request from {message}, enter _acc {message} to accept.\n----------\n>> ', end='')
        elif status == "_requestcreated":
            print(f'\rFriend request to {message} sent.\n----------\n>> ', end='')
        elif status == "_requestexists":
            print(f'\rYou have already sent {message} a friend request.\n----------\n>> ', end='')
        elif status == "_requestaccepted":
            print(f'\rYour friend request has been accepted by {message}.\n----------\n>> ', end='')
        elif status == "_requestsentaccept":
            print(f'\rYou are now friends with {message}.\n----------\n>> ', end='')
        elif status == "_alreadyfriends":
            print(f'\rYou already have {message} in your friend list.\n----------\n>> ', end='')
        elif status == "_notfriends":
            print(f'\rYou are not friends with {message} yet.\n----------\n>> ', end='')
        elif status == '_acceptfile':
            sender, filename, filesize, filedata = message.split(b'|', 3)
            sender = sender.decode('utf-8')
            filename = filename.decode('utf-8')
            filesize = int(filesize.decode('utf-8'))
            print(f'\rYou received a file from {sender} named {filename} with size of {filesize} bytes.\n----------\n>> ', end='')
            while len(filedata) < filesize:
                if filesize - len(filedata) > 65536:
                    filedata += sock_client.recv(65536)
                else:
                    filedata += sock_client.recv(filesize - len(filedata))
                    break
            
            if not os.path.exists('files'):
                os.mkdir('files')
            with open(f'files/{filename}', 'wb') as f:
                f.write(filedata)

        else:
            print(f"\r{message}\n----------\n>> ", end='')

def main():
    username = input('Set username: ').strip().lstrip('_').replace('|', '')
    print(f'Username set: {username}')

    sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_client.connect(remote_address)

    sock_client.send(username.encode('utf-8'))

    thread_receive = Thread(target=receive_message, args=(sock_client,))
    thread_receive.start()

    while True:
        dest = input('----------\nAvailable commands:\n_bcast <message>\tBroadcast a message\n<recipient> <message>\tSend a message to recipient\n_req <username>\tSend a friend request to username\n_acc <username>\tAccept a friend request from username\n_sendfile <username> <path>\tSend a file at path to username\n_quit\tExit the app\n----------\n>> ')
        command = dest.split(" ", 1)
        if command[0] == '_quit':
            sock_client.close()
            break
        elif command[0] == '_sendfile':
            username, path = dest.split(" ", 2)[1:]
            size = os.path.getsize(path)
            filedata = f'_sendfile|{username}|{path.split("/")[-1]}|{size}|'.encode('utf-8')
            with open(path, 'rb') as f:
                filedata += f.read()
            
            sock_client.sendall(filedata)
        else:
            sock_client.send(f'{command[0]}|{command[1]}'.encode('utf-8'))

if __name__ == '__main__':
    main()
