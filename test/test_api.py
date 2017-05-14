# coding=utf-8
import json
from http.client import InvalidURL
from urllib.parse import parse_qs, urlsplit

import pytest
from asynctest import CoroutineMock

from acme.api import Api
from acme.errors.api import ApiError


def test_call_api_with_inexistent_path(api):
    with pytest.raises(InvalidURL):
        api.foo()


def test_build_url(api, config):
    path = 'purchases_by_user'
    params = {
        'limit': 10,
        'games': 'yes'
    }
    user = 'some_user'

    url = api._build_url(path, params, username=user)

    # We can't simply test if url == 'expected_url' because the query
    # parameters may not be in the order we assume, so let's break it
    # apart and test each component individually.

    parsed = urlsplit(url)

    assert parsed.path == '/api/' + api._paths[path].format(username=user)

    p = parse_qs(parsed.query)
    assert p == {'limit': ['10'], 'games': ['yes']}

    result = parsed.scheme + '://' + parsed.netloc + '/api/'
    assert result == config['API_BASE_URL']


def test_build_url_with_no_params(api):
    """
    If no query string parameters are passed, the resulting URL should
    have none either.
    """

    url = api._build_url('purchases_by_user', username='foo')

    parsed = urlsplit(url)

    p = parse_qs(parsed.query)
    assert p == {}


@pytest.mark.asyncio
async def test_cache(config, http, cache):
    """
    Make sure an API method, when called more than once with the same
    parameters, only results in one HTTP call, since the second time it
    gets the data from the cache.
    """
    http.get = CoroutineMock()
    text = '{}'
    http.get.return_value = {'status': 200, 'text': text}
    api = Api(config, http, cache)

    user = 'some_user'
    params = {'limit': 10}

    await api.purchases_by_user(params, username=user)
    await api.purchases_by_user(params, username=user)

    path = api._paths['purchases_by_user'].format(username=user)
    url = config['API_BASE_URL'] + path + '?limit=10'
    api.http.get.assert_called_once_with(url)


@pytest.mark.asyncio
async def test_failing_api_call(config, http, cache):
    http.get = CoroutineMock()
    http.get.return_value = {'status': 500}
    api = Api(config, http, cache)

    product_id = 10
    params = {'limit': 10}

    with pytest.raises(ApiError):
        await api.purchases_by_product(params, product_id=product_id)


async def test_purchases_by_user(config, http, cache):
    """
    I will only test this API method since the others all run the same
    code and the HTTP call result is mocked by me. Thus, it doesnt' make
    much sense to test all the methods unless I were to test the real
    API, which returns different results for each of the methods.
    """
    http.get = CoroutineMock()
    text = '{}'
    http.get.return_value = {'status': 200, 'text': text}
    api = Api(config, http, cache)

    user = 'some_user'
    params = {'limit': 10}

    result = await api.purchases_by_user(params, username=user)

    assert result == json.loads(text)

    path = api._paths['purchases_by_user'].format(username=user)
    url = config['API_BASE_URL'] + path + '?limit=10'
    api.http.get.assert_called_with(url)
