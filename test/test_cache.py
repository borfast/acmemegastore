# coding=utf-8
from aiohttp.test_utils import unittest_run_loop

from acme.cache import MemoryCache
from test.AcmeMegastoreTestCase import AcmeMegastoreTestCase


class TestMemoryCache(AcmeMegastoreTestCase):
    """
    For brevity I will only test the memory cache and will not test every
    single scenario.
    """
    def setUp(self):
        super().setUp()
        self.cache = MemoryCache()

    @unittest_run_loop
    async def test_has_when_key_does_not_exist(self):
        self.assertFalse(await self.cache.has('foo'))

    @unittest_run_loop
    async def test_has_when_key_exists(self):
        self.cache._cache['foo'] = 'I exist!'
        self.assertTrue(await self.cache.has('foo'))

    @unittest_run_loop
    async def test_get(self):
        value = 'I exist!'
        self.cache._cache['foo'] = value
        self.assertEqual(await self.cache.get('foo'), value)

    @unittest_run_loop
    async def test_set(self):
        value = 'I am set!'
        await self.cache.set('foo', value)
        self.assertEqual(self.cache._cache['foo'], value)

    @unittest_run_loop
    async def test_delete(self):
        value = 'I exist!'
        self.cache._cache['foo'] = value
        await self.cache.delete('foo')
        self.assertNotIn('foo', self.cache._cache)
