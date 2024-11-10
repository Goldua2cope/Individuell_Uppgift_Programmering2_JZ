import socket, threading, datetime

HOST = '127.0.0.1'
PORT = 62555

alias = input('Choose an alias:\n')

def receive() -> None:
    '''Receives and prints messages from the server.'''
    while True:
        try:
            message = client_sock.recv(1024).decode('utf-8')
            if not message: #handles graceful disconnection
                print('Disconnected from server.')
                break
            if message == 'alias':
                client_sock.send(alias.encode('utf-8'))
            else:
                now = str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M'))
                print(now.ljust(10,' '), message)
        except OSError as e:
            break
        except Exception as e:
            print(f'Server Error: {e}')
            break

def write() -> None:
    '''Send messages to the server.'''
    while True:
        try:
            message = '{}:{}'.format(alias, input(""))
            if message.endswith('exit'):
                client_sock.close()
                print('Disconnected from server.')
                break
            client_sock.send(message.encode('utf-8'))
        except ConnectionResetError:
            print('Error sending to server. Disconnected from the server.')
            break
        except Exception as e:
            print(f'Unexpected error sending. {e}')
            continue # Prompts user until he/she wants to exit

if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_sock:
        try:
            client_sock.connect((HOST, PORT))

            receive_thread = threading.Thread(target=receive, daemon=True)
            receive_thread.start()

            write_thread = threading.Thread(target=write, daemon=True)
            write_thread.start()

            receive_thread.join()
            write_thread.join()
        except ConnectionRefusedError:
            print('Unable to connect to the server.')
        except Exception as e:
            print(f'Unexpected error: {e}')
