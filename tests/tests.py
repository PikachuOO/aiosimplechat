import asyncio
import unittest
import random
import server


def asynctest(f):
    def wrapper(*args, **kwargs):
        print('Testing {}'.format(f.__name__))
        # Create a new event_loop for each test. They cannot run in the same loop.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop = asyncio.get_event_loop()
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop.run_until_complete(future)
        print('Test {} completed'.format(f.__name__))
    return wrapper

used_ports = []


class TestServer(unittest.TestCase):
    def setUp(self):
        def generate_port():
            port = random.randint(8000, 9000)
            if port in used_ports:
                generate_port()
            used_ports.append(port)
            return port

        port = generate_port()
        self.mainserver = server.Server(host='127.0.0.1', port=port)
        print(used_ports)

    @asynctest
    def test_if_server_runs(self):
        print('Testing if_server_runs...')
        yield from self.mainserver.run_server()
        self.assertTrue(self.mainserver.server)
        self.assertEqual(type(self.mainserver.server), asyncio.base_events.Server)
        yield from self.mainserver.run_server()
        self.assertRaises(OSError)
        print('Test if_server_runs completed')

    @asynctest
    def test_if_connected(self):
        yield from self.mainserver.run_server()
        reader, writer = yield from asyncio.open_connection(self.mainserver.host, self.mainserver.port)
        msg = yield from reader.readline()
        self.assertIn(b'Welcome to this server', msg)

    @asynctest
    def test_if_message_is_sent_to_clients(self):
        yield from self.mainserver.run_server()
        reader, writer = yield from asyncio.open_connection(self.mainserver.host, self.mainserver.port)
        writer.write(b'test_message\n')
        while True:
            msg = yield from reader.readline()
            print(msg)
            if not b'Welcome to this server' in msg:
                self.assertIn(b'test_message\n', msg)
                break

    @asynctest
    def test_spread_the_word(self):
        yield from self.mainserver.run_server()
        reader, writer = yield from asyncio.open_connection(self.mainserver.host, self.mainserver.port)
        yield from self.mainserver.spread_the_word('Testrunner', b'Spreading the word')
        while True:
            msg = yield from reader.readline()
            if not b'Welcome to this server' in msg:
                self.assertIn(b'Spreading the word', msg)
                break

    @asynctest
    def test_if_eof_is_set(self):
        yield from self.mainserver.run_server()
        reader, writer = yield from asyncio.open_connection(self.mainserver.host, self.mainserver.port)
        self.mainserver.close_clients()
        while not reader.at_eof():
            yield from reader.readline()
        self.assertTrue(reader.at_eof())

    @asynctest
    def test_if_user_gets_disconnected_on_close(self):
        yield from self.mainserver.run_server()
        reader, writer = yield from asyncio.open_connection(self.mainserver.host, self.mainserver.port)
        writer.write(b'close()\n')
        while not reader.at_eof():
            yield from reader.readline()
        self.assertFalse(self.mainserver.clients)
