from ldotcommons import messaging
from ldotcommons import fetchers

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86) Home software (KHTML, like Gecko)'


class Http(messaging.Source):
    def __init__(self, url):
        self._url = url

        self._fetcher = fetchers.UrllibFetcher(
            cache=True,
            headers={'User-Agent': USER_AGENT})
        self._m = None

    def recv(self, data=None):
        if data:
            raise Exception('POST not supported')

        if not self._m:
            self._m = self._fetcher.fetch(self._url)

        return self._m
