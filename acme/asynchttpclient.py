# coding=utf-8
import aiohttp


class AsyncHttpClient:
    """
    This could be turned into an abstract class so that we could easily replace
    the implementation without having to change the code that uses it.
    In case you're wondering why we don't use something like the
    excellent requests library, it's simple: it's not asynchronous and thus
    would block when fetching data from the data API, which would negate all
    the work of using aiohttp / asyncio and its benefits. We could probably
    still use it but we would have to use an executor from
    concurrent.futures but for demonstration purposes it's not worth the
    effort.
    """
    async def get(self, url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                result = {'status': resp.status}

                if 200 <= resp.status <= 299:
                    result['text'] = await resp.text()

                return result
