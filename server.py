import asyncio
from collections import namedtuple

Client = namedtuple('Client', 'peername reader writer')


class Server:
    clients = []
    server = None

    def __init__(self, loop):
        self.loop = loop

    @asyncio.coroutine
    def run_server(self):
        self.server = yield from asyncio.start_server(self.client_connected, '127.0.0.1', 8089)
        print('Running server on default host and port')
        return self.server

    @asyncio.coroutine
    def spread_the_word(self, peername, msg):
        print('Got message "{}", spreading the word'.format(msg.decode().strip()))
        for client in self.clients:
            print('Sending to {}'.format(client.peername))
            client.writer.write('{}: {}\n'.format(peername, msg.decode().strip()).encode())
        return

    def close_clients(self):
        print('Sending EndOfFile to all clients to close them.')
        for client in self.clients:
            client.writer.write_eof()

    @asyncio.coroutine
    def client_connected(self, reader, writer):
        print('Client connected.')
        peername = writer.transport.get_extra_info('peername')
        new_client = Client(peername, reader, writer)
        self.clients.append(new_client)
        writer.write('Welcome to this server client: {}\n'.format(peername).encode())
        while not reader.at_eof():
            try:
                msg = yield from reader.readline()
                if msg:
                    print('Server Received: "{}"'.format(msg.decode().strip()))
                    if not msg.decode().strip() == 'close()':
                        yield from self.spread_the_word(peername, msg)
                    else:
                        print('User {} disconnected'.format(peername))
                        self.clients.remove(new_client)
                        for client in self.clients:
                            client.writer.write('{}: User disconnected\n'.format(peername).encode())
            except ConnectionResetError as e:
                print('ERROR: {}'.format(e))
                self.clients.remove(new_client)
                return

    def close(self):
        self.close_clients()
        self.loop.stop()


def main():
    loop = asyncio.get_event_loop()
    mainserver = Server(loop)
    asyncio.async(mainserver.run_server())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print('receieved interrupt, closing')
        mainserver.close()
    finally:
        loop.close()


if __name__ == '__main__':
    main()