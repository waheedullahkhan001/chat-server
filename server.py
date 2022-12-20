# Asynchronous chat server

import asyncio
import socket


HEADER_SIZE = 64

clients = []


async def send_text(sock: socket.socket, text: str):
    """Send text to socket.

    The text is first encoded to bytes and then prefixed with a header
    """
    loop = asyncio.get_event_loop()
    payload = text.encode('utf8')
    header = f'{len(payload):<{HEADER_SIZE}}'.encode('utf8')
    await loop.sock_sendall(sock, header + payload)

async def recv_text(sock: socket.socket) -> str:
    """Receive text from socket.
    
    The header is first received and then the payload is received
    and decoded to a string.
    """
    loop = asyncio.get_event_loop()
    
    # Receive header and get payload size
    header = b''
    while len(header) < HEADER_SIZE:
        header += await loop.sock_recv(sock, HEADER_SIZE - len(header))
    payload_size = int(header.decode('utf8').strip())

    # Receive payload
    payload = b''
    while len(payload) < payload_size:
        payload += await loop.sock_recv(sock, payload_size - len(payload))
    return payload.decode('utf8')

async def handle_client(client: socket.socket):
    """Handle client connection.
    
    It receives messages from the client and sends them to all other clients.
    """
    message = None
    try:
        while True:
            if message is None:
                message = await recv_text(client)
                print(message)
            else:
                # Send message to all clients
                for c in clients:
                    await send_text(c, message)
                message = None
    except ConnectionError:
        pass
    client.close()
    clients.remove(client)

async def run_server():
    """Run the server.
    
    It creates a socket and listens for connections. When a connection is
    received, it is added to the list of clients and a task is created to
    handle the client.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', 8098))
    server.listen(8)
    server.setblocking(False)

    loop = asyncio.get_event_loop()

    print('Server started')

    while True:
        client, _ = await loop.sock_accept(server)
        clients.append(client)
        loop.create_task(handle_client(client))


if __name__ == '__main__':
    asyncio.run(run_server())
