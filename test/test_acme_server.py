# coding=utf-8

from aiohttp.test_utils import unittest_run_loop

from test.AcmeMegastoreTestCase import AcmeMegastoreTestCase


class TestAcmeServer(AcmeMegastoreTestCase):
    @unittest_run_loop
    async def test_no_username(self):
        request = await self.client.request('GET', '/api/recent_purchases/')
        request.close()
        assert request.status == 404

    # # a vanilla example
    # def test_example(self):
    #     async def test_get_route():
    #         url = root + "/"
    #         resp = await self.client.request("GET", url, loop=loop)
    #         assert resp.status == 200
    #         text = await resp.text()
    #         assert "Hello, world" in text
    #
    #     self.loop.run_until_complete(test_get_route())
