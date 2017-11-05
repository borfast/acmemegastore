# coding=utf-8
import json
from http.client import InvalidURL
from urllib.parse import urljoin, urlencode

# from aiohttp.errors import InvalidURL

from .asynchttpclient import AsyncHttpClient
from .cache import AbstractCache
from .errors.api import ApiError


class Api:
    """
    A wrapper for the data API.
    """

    def __init__(self, config: dict, http: AsyncHttpClient,
                 cache: AbstractCache):
        # Group the API paths here so we don't have to repeat them
        # everywhere and risk causing problems by trying to access a wrong
        # path.
        self._paths = {
            'user': 'users/{username}',
            'purchases_by_user': 'purchases/by_user/{username}',
            'purchases_by_product': 'purchases/by_product/{product_id}',
            'products': 'products/{product_id}'
        }
        self.config = config
        self.http = http
        self.cache = cache

    def __getattr__(self, name: str):
        """
        Instead of implementing each and every API method here, we simply add
        them to the _paths dictionary and let Python's magic do its thing. This
        way we can (hopefully) add future API methods without much work (
        assuming they are not much different from the current ones).
        """

        if name not in self._paths:
            raise InvalidURL('Unrecognised method/path: {}'.format(name))

        async def _api_method(*args, **kwargs) -> object:
            """
            Grab the query string parameters from the first positional
            argument, build the required URL and make an HTTP call to it.

            Before making any HTTP requests, it checks the cache to see if
            we already have that data. The cache expiration timeout can be
            set in the settings. Cache invalidation should be handled
            where data is manipulated, i.e., when a new user is created or a
            new purchase registered, the relevant pieces of data in the
            cache should be invalidated.

            Loads the response directly into an object for simplicity. This is
            a huge assumption, of course: assumption that we get a JSON string
            and only a JSON string, no other text or anything else.
            """
            params = args[0] if len(args) == 1 else None
            url = self._build_url(name, params, **kwargs)

            if await self.cache.has(url):
                cache_result = await self.cache.get(url)
                return json.loads(cache_result)

            resp = await self.http.get(url)
            if resp['status'] != 200:
                raise ApiError('Unknown error fetching data from the API. '
                               'Error code: {}'.format(resp['status']))

            await self.cache.set(url, resp['text'])

            return json.loads(resp['text'])

        return _api_method

    def _build_url(self, name: str, params: dict = None, **kwargs) -> str:
        """
        Build the URL for the given resource name being accessed and a query
        string using the given parameters. kwargs is used to fill in the
        variable URL parts in the required self._paths path. For example,
        if you want to access /api/users/{username}, you pass
        username=some_user so you get the path /api/users/some_user.
        """
        name = self._paths[name].format(**kwargs)
        url = urljoin(self.config['API_BASE_URL'], name)

        if params is not None:
            params = urlencode(params)
            url += '?' + params

        return url
