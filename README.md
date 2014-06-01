aiosimplechat
=============

Very simple client-server chat application.

Trying out Python's new asyncio module to create a chat application.

### Requirements:
Python 3.3+

### Usage:
Start server.py

Start as many client.py instances as you like and start chatting to yourself!

### Goal:
See if it's possible to import these into an actual program to do real easy network communication.


It seems pretty performant.
With python3 in the aiosimplechat directory:
```python
from server import Server
from client import Client
import asyncio

server = Server()
asyncio.async(run_server())
  
for x in range(1000):
    client = Client()
    asyncio.async(client.connect())
    
loop = asyncio.get_event_loop()
loop.run_forever()
```

The initial load takes a second, but the messages being relayed are near instant.

  
Comments/criticism are/is very welcome :)
