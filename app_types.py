"""
Description:
    Types used by the crawler and processor.

Created:
    2024-09-28
"""

import asyncio


class AsyncList:
    """
    Simple asyncronous list class that allows for thread safe
    appending and popping.
    """

    def __init__(self):
        self._list = []
        self._lock = asyncio.Lock()

    async def append(self, item):
        async with self._lock:
            self._list.append(item)

    async def get_all(self):
        async with self._lock:
            return list(self._list)

    async def pop(self):
        async with self._lock:
            if self._list:
                return self._list.pop(0)
            return None
