import asyncio
from collections import namedtuple

Client = namedtuple('Client', 'reader writer')


class Server:
    clients = {}
    server = None

    def __init__(self, host='127.0.0.1', port=8089):
        self.loop = asyncio.get_event_loop()
        self.host = host
        self.port = port
        self.clients = {}

    @asyncio.coroutine
    def run_server(self):
        try:
            self.server = yield from asyncio.start_server(self.client_connected, self.host, self.port)
            print('Running server on {}:{}'.format(self.host, self.port))
        except OSError:
            print('Cannot bind to this port! Is the server already running?')
            self.loop.stop()

    @asyncio.coroutine
    def send_to_client(self, peername, msg):
        client = self.clients[peername]
        print('Sending to {}'.format(peername))
        client.writer.write('{}\n'.format(msg).encode())
        return

    @asyncio.coroutine
    def send_to_all_clients(self, peername, msg):
        print('Got message "{}", send to all clients'.format(msg))
        for client_peername, client in self.clients.items():
            print('Sending to {}'.format(client_peername))
            client.writer.write('{}: {}\n'.format(peername, msg).encode())
        return

    def close_clients(self):
        print('Sending EndOfFile to all clients to close them.')
        for peername, client in self.clients.items():
            client.writer.write_eof()

    def receive_private_msg(self, msg):
        pass

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        print('Client connected.')
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(reader, writer)
        self.clients[peername] = new_client
        yield from self.send_to_client(peername, 'Welcome to this server client: {}'.format(peername))
        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                if msg:
                    msg = msg.decode().strip()
                    print('Server Received: "{}"'.format(msg))
                    if not msg == 'close()':
                        if msg.startswith('@private'):
                            self.receive_private_msg(msg)  # Might need yield from if it becomes a coroutine
                        else:
                            yield from self.send_to_all_clients(peername, msg)
                    else:
                        print('User {} disconnected'.format(peername))
                        del self.clients[peername]
                        self.send_to_all_clients(peername, 'User disconnected')
                        writer.write_eof()
            except ConnectionResetError as e:
                print('ERROR: {}'.format(e))
                del self.clients[peername]
                return

    def close(self):
        self.close_clients()
        self.loop.stop()


def main():
    loop = asyncio.get_event_loop()
    mainserver = Server()
    asyncio.async(mainserver.run_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('Received interrupt, closing')
        mainserver.close()
    finally:
        loop.close()


if __name__ == '__main__':
    main()