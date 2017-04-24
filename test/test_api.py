# coding=utf-8
import json
from http.client import InvalidURL
from urllib.parse import parse_qs, urlsplit

import pytest
from aiohttp.test_utils import unittest_run_loop
from asynctest import CoroutineMock

from acme.errors.api import ApiError
from test.AcmeMegastoreTestCase import AcmeMegastoreTestCase


class TestApi(AcmeMegastoreTestCase):

    def test_call_api_with_inexistent_path(self):
        with pytest.raises(InvalidURL):
            self.api.foo()

    def test_build_url(self):
        path = 'purchases_by_user'
        params = {
            'limit': 10,
            'games': 'yes'
        }
        user = 'some_user'

        url = self.api._build_url(path, params, username=user)

        # We can't simply test if url == 'expected_url' because the query
        # parameters may not be in the order we assume, so let's break it
        # apart and test each component individually.

        parsed = urlsplit(url)

        assert parsed.path == '/api/' + self.api._paths[path].format(
            username=user)

        p = parse_qs(parsed.query)
        assert p == {'limit': ['10'], 'games': ['yes']}

        result = parsed.scheme + '://' + parsed.netloc + '/api/'
        assert result == self.config['API_BASE_URL']

    def test_build_url_with_no_params(self):
        """
        If no query string parameters are passed, the resulting URL should
        have none either.
        """

        url = self.api._build_url('purchases_by_user', username='foo')

        parsed = urlsplit(url)

        p = parse_qs(parsed.query)
        assert p == {}

    @unittest_run_loop
    async def test_cache(self):
        """
        Make sure an API method, when called more than once with the same
        parameters, only results in one HTTP call, since the second time it
        gets the data from the cache.
        """
        self.http.get = CoroutineMock()
        text = '{}'
        self.http.get.return_value = {'status': 200, 'text': text}

        user = 'some_user'
        params = {'limit': 10}

        await self.api.purchases_by_user(params, username=user)
        await self.api.purchases_by_user(params, username=user)

        path = self.api._paths['purchases_by_user'].format(username=user)
        url = self.config['API_BASE_URL'] + path + '?limit=10'
        self.http.get.assert_called_once_with(url)

    @unittest_run_loop
    async def test_purchases_by_user(self):
        """
        I will only test this API method since the others all run the same
        code and the HTTP call result is mocked by me. Thus, it doesnt' make
        much sense to test all the methods unless I were to test the real
        API, which returns different results for each of the methods.
        """
        self.http.get = CoroutineMock()
        text = '{}'
        self.http.get.return_value = {'status': 200, 'text': text}

        user = 'some_user'
        params = {'limit': 10}

        result = await self.api.purchases_by_user(params, username=user)

        assert result == json.loads(text)

        path = self.api._paths['purchases_by_user'].format(username=user)
        url = self.config['API_BASE_URL'] + path + '?limit=10'
        self.http.get.assert_called_with(url)

    @unittest_run_loop
    async def test_failing_api_call(self):

        self.http.get = CoroutineMock()
        self.http.get.return_value = {'status': 500}

        product_id = 10
        params = {'limit': 10}

        with pytest.raises(ApiError):
            await self.api.purchases_by_product(params, product_id=product_id)
