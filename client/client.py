import socket
import sys
from threading import Thread

remote_address = ('127.0.0.1', 6666)

position = 0

def receive_message(sock_client):
    while True:
        data = sock_client.recv(65535)
        if len(data) == 0:
            break
        
        print(data.decode('utf-8'))

def main():
    username = input('Set username: ').strip().lstrip('_')
    print(f'Username set: {username}')

    sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_client.connect(remote_address)

    sock_client.send(username.encode('utf-8'))

    thread_receive = Thread(target=receive_message, args=(sock_client,))
    thread_receive.start()

    while True:
        dest = input('Set recipient username (_bcast to broadcast, _quit to quit): ')
        if dest == '_quit':
            sock_client.close()
            break
        
        message = input('Enter message: ')
        sock_client.send(f'{dest}|{message}'.encode('utf-8'))

if __name__ == '__main__':
    main()