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
            return list(self._list)  # Return a copy of the list

    async def pop(self):
        async with self._lock:
            if self._list:
                return self._list.pop(0)
            return None


def pattern_filter(
    urls: List[str],
    regex_patterns: List[str],
) -> List[str]:
    """
    Searches a list of urls for regular expression patterns and keeps
    only those that match one of the patterns. This is a whitelist
    style pattern matching function.
    """
    regex_patterns = [re.compile(pattern) for pattern in regex_patterns]
    filtered_urls = []
    for url in urls:
        for pattern in regex_patterns:
            match = pattern.search(url)
            if match is not None:
                filtered_urls.append(url)
                break

    print("these are the filtered urls:", filtered_urls)
    return filtered_urls


