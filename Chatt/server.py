import socket, threading,sys

HOST = '127.0.0.1'
PORT = 62555

clients: list[socket.socket] = []
aliases: list[str] = []

lock = threading.Lock()
running_event = threading.Event()

def broadcast(message: bytes) -> None:
    '''Broadcast message to all connected clients.'''
    with lock:
        for client in clients:
            try:
                client.send(message)
            except ConnectionResetError:
                print(f'Unexpected error broadcasting message to client: {client}. No connection to client.')
                remove_client(client)
            except Exception as e:
                print(f'Unexpected error broadcasting message to client: {client}. {e}')
                remove_client(client)

def remove_client(client: socket.socket) -> None:
    '''Removes a client and its alias, disconnects client, notifies all clients.'''
    try:
        with lock:
            index = clients.index(client)
            clients.remove(client)
            alias = aliases[index]
            aliases.remove(alias)
            client.close()
        broadcast(f'{alias} left the chat.'.encode('utf-8'))
        print(f'Removed client: {alias}')
    except ValueError: # Occurs primarily when using keyboard interupt to terminate program
        pass
    except Exception as e:
        print(f'Error removing client: {client}. {e}')

def handle_client_connection(client: socket.socket) -> None:
    '''Handle communication with connected client.'''
    while running_event.is_set():
        try:
            message = client.recv(1024)
            if not message: #handles graceful disconnection
                break
            else:
                broadcast(message)
        except ConnectionResetError: # handles ungraceful disconnection
            print(f'Unexpected Error: Connection to {client} not found.')
            break
        except OSError: # Occurs primarily when using keyboard interupt to terminate program
            break
        except Exception as e:
            print(f'Unexpected error handling client: {e}')
            break
    remove_client(client)

def handle_new_connection() -> None:
    '''Accepts new connections and creats thread to handle them.'''
    sock.settimeout(1.0)
    while running_event.is_set():
        try:
            client, addr = sock.accept()
            print(f'Connected with {str(addr)}')

            client.send('alias'.encode('utf-8'))
            alias = client.recv(1024).decode('utf-8')
            with lock:
                clients.append(client)
                aliases.append(alias)
                    
            thread = threading.Thread(target=handle_client_connection, args=(client,), daemon=True)
            thread.start()

            print(f'Name of the client is {alias}')
            client.send('Connected to the server.'.encode('utf-8'))
            broadcast(f'{alias} joined the chat.'.encode('utf-8'))
        except socket.timeout:
            continue
        except Exception as e:
            print(f'Connection could not be established with: {e}')
            continue

if __name__ == '__main__':
    running_event.set()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.listen()
        print(f'Server listening on {HOST}:{PORT}...')
        try:
            handle_new_connection()
        except KeyboardInterrupt:
            running_event.clear()
            print('Server shutting down...')
            print('Resources are being cleared...')
            with lock:
                for client in clients:
                    client.close()
                clients.clear()
                aliases.clear()
            print('Succesfully shut down.')
            sys.exit()
