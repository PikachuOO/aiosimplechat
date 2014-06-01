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
With ipython3 in the aiosimplechat directory:
```
from client import Client
import asyncio

for x in range(1020):  # 1024 is hardlimit, can't seem to be able to change it.
  client = Client()
  asyncio.async(client.connect())
  
loop = asyncio.get_event_loop()
loop.run_forever()
```

The initial load takes a second, but the messages being relayed are near instant.

  
Comments/criticism are/is very welcome :)
