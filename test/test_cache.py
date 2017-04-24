# coding=utf-8
"""
For brevity I will only test the memory cache and will not test every
single scenario.
"""


async def test_has_when_key_does_not_exist(cache):
    assert await cache.has('foo') is False


async def test_has_when_key_exists(cache):
    cache._cache['foo'] = 'I exist!'
    assert await cache.has('foo')


async def test_get(cache):
    value = 'I exist!'
    cache._cache['foo'] = value
    assert await cache.get('foo') == value


async def test_set(cache):
    value = 'I am set!'
    await cache.set('foo', value)
    assert cache._cache['foo'] == value


async def test_delete(cache):
    value = 'I exist!'
    cache._cache['foo'] = value
    await cache.delete('foo')
    assert 'foo' not in cache._cache
