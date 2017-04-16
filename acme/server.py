# coding=utf-8
import asyncio

import aioredis
import uvloop
from aiohttp import web

from . import settings
from .megastore import Megastore
from .api import Api
from .asynchttpclient import AsyncHttpClient
from .cache import RedisCache

if __name__ == '__main__':
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()

    # Set up all the dependencies to create the Megastore object.

    config = settings.get_config()
    http = AsyncHttpClient()

    # The ugly part of Python's asynchronous stuff :(
    create_redis_coro = aioredis.create_redis((config['REDIS_HOST'],
                                               config['REDIS_PORT']),
                                              db=config['REDIS_DB'],
                                              loop=loop)
    create_redis_future = asyncio.ensure_future(create_redis_coro)
    loop.run_until_complete(create_redis_future)
    redis = create_redis_future.result()

    cache = RedisCache(redis, config['CACHE_EXPIRATION'])
    api = Api(config, http, cache)

    handler = Megastore(config, api, loop)

    app = web.Application(loop=loop)
    app.router.add_route('get', '/api/recent_purchases/{username}',
                         handler.recent_purchases)
    web.run_app(app)
