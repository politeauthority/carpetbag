import asyncio
from carpetbag import CarpetBag as cp

loop = asyncio.get_event_loop()
test = cp()
test2 = loop.run_until_complete(test.get_gud_proxies())
print(test2)
loop.close()
