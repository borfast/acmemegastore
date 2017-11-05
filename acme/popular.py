# coding=utf-8
import asyncio
from operator import itemgetter

from .api import Api


class Popular:
    def __init__(self, api: Api, loop: asyncio.AbstractEventLoop):
        self.api = api
        self.loop = loop

    async def popular(self, user: str) -> list:
        recent = await self.api.purchases_by_user({'limit': 5}, username=user)

        # Let's use a dict so it's easier to check which products are
        # already in there by using the product ID as the key. We will then
        # drop the keys and convert the dict to a list to respect the
        # desired format.
        popular = {}

        for purchase in recent['purchases']:
            product_id = purchase['product_id']  # Easier to type.

            # No need to do this for products already in the list.
            if product_id in popular:
                continue

            popular[product_id] = await self._product_info(product_id)

        # Sort the list according to the number of purchases for each product.
        popular = sorted(popular.values(), key=itemgetter('count'),
                         reverse=True)

        def remove_count(product):
            del product['count']
            return product

        popular = map(remove_count, popular)

        return list(popular)

    async def _product_info(self, product_id: int) -> dict:
        """
        Executes the two API calls in parallel and waits for them both to
        finish. The sequential way of doing it would be this:
         purchases = await self.api.purchases_by_product(product_id=product_id)
         product = await self.api.products(product_id=product_id)
         purchases = purchases['purchases']
         product = product['product']
        """

        results = await asyncio.gather(
            self.api.purchases_by_product(product_id=product_id),
            self.api.products(product_id=product_id),
            loop=self.loop
        )
        purchases = results[0]['purchases']
        product = results[1]['product']

        # List of all the recent buyers of this product. Use a set to
        # remove duplicates - the end user doesn't really care which people
        # bought a product more than once.
        product['recent'] = list(set([p['username'] for p in purchases]))

        # Count how many purchases this product had. We need this
        # information so we can sort the final list of products but we don't
        # want it in the list, so we need to remove it after we build the list.
        product['count'] = len(purchases)

        return product
