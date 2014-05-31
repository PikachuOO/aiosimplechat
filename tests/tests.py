import unittest
import asyncio
import server


class TestServer(unittest.TestCase):
    def setUp(self):
        # Tests can't run on the same eventloop. Create a new eventloop for each test.
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.loop = asyncio.get_event_loop()
        self.mainserver = server.Server(self.loop)

    def test_if_server_runs(self):
        self.loop.run_until_complete(self.mainserver.run_server())
        self.assertTrue(self.mainserver.server)

    def test_if_message_is_sent_to_clients(self):
        self.loop.run_until_complete(self.mainserver.run_server())
        reader, writer = yield from self.loop.create_connection('127.0.0.1', 8089)
        writer.write(b'test_message\n')
        msg = yield from reader.readline()
        self.assertIn(b'test_message\n', msg)

    def test_if_eof_is_set(self):
        self.loop.run_until_complete(self.mainserver.run_server())
        reader, writer = yield from self.loop.create_connection('127.0.0.1', 8089)
        self.mainserver.close_clients()
        self.assertTrue(reader.at_eof())

    def tearDown(self):
        self.mainserver.close()
