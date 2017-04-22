# coding=utf-8

from aiohttp.test_utils import unittest_run_loop

from test.AcmeMegastoreTestCase import AcmeMegastoreTestCase


class TestAcmeServer(AcmeMegastoreTestCase):
    @unittest_run_loop
    async def test_no_username(self):
        request = await self.client.request('GET', '/api/recent_purchases/')
        request.close()
        assert request.status == 404
