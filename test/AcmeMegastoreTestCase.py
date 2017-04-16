# coding=utf-8
import asyncio

import uvloop
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase

from acme.megastore import Megastore
from acme.api import Api
from acme.asynchttpclient import AsyncHttpClient
from acme.cache import MemoryCache


class AcmeMegastoreTestCase(AioHTTPTestCase):
    def setUp(self):
        # Use the same event loop we will use in production.
        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

        self.config = {
            'ACME_DEBUG': True,
            'API_BASE_URL': 'http://localhost:6000/api/'
        }

        self.http = AsyncHttpClient()
        cache = MemoryCache()
        self.api = Api(self.config, self.http, cache)

        super().setUp()

    @asyncio.coroutine
    def get_application(self):
        # it's important to use the loop passed here.
        self.app = web.Application(loop=self.loop)

        self.acme_handler = Megastore(self.config, self.api, self.loop)
        self.app.router.add_route('get', '/api/recent_purchases/{username}',
                                  self.acme_handler.recent_purchases)
        return self.app
