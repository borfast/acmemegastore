# coding=utf-8
import asyncio
import json
import os

import pytest
import uvloop
from aiohttp import web
from asynctest import CoroutineMock

from acme.api import Api
from acme.asynchttpclient import AsyncHttpClient
from acme.cache import MemoryCache
from acme.megastore import Megastore


@pytest.fixture(scope='session', autouse=True)
def setup_loop():
    """ Use the same event loop we will use in production. """
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


@pytest.fixture(scope='session')
def config():
    return {
        'ACME_DEBUG': True,
        'API_BASE_URL': 'http://localhost:6000/api/'
    }


@pytest.fixture
def http():
    result_http = AsyncHttpClient()
    result_http.get = CoroutineMock()

    return result_http


@pytest.fixture
def cache():
    return MemoryCache()


@pytest.fixture
def api(config, http, cache, purchases_by_user, purchases_by_product,
        products):
    """ TODO: For some reason it's not working, will have to debug later. """
    result_api = Api(config, http, cache)
    result_api.purchases_by_user = CoroutineMock()
    result_api.purchases_by_product = CoroutineMock()
    result_api.products = CoroutineMock()
    result_api.purchases_by_user.return_value = purchases_by_user
    result_api.purchases_by_product.side_effect = purchases_by_product
    result_api.products.side_effect = products

    return result_api


@pytest.fixture
def handler(config, api, loop):
    return Megastore(config, api, loop)


@pytest.fixture
def app(loop, handler):
    application = web.Application(loop=loop)

    application.router.add_route('get', '/api/recent_purchases/{username}',
                                 handler.recent_purchases)
    return application


@pytest.fixture(scope='session')
def purchases_by_user():
    return _load_json('purchases_by_user.json')


@pytest.fixture(scope='session')
def purchases_by_product():
    return _load_json('purchases_by_product.json')


@pytest.fixture(scope='session')
def products():
    return _load_json('products.json')


def _load_json(filename):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'fixtures', filename)
    with open(path) as fp:
        return json.load(fp)
