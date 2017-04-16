# coding=utf-8
from aiohttp.test_utils import unittest_run_loop
from unittest.mock import call
from asynctest import CoroutineMock

from acme.popular import Popular
from test import fixtures
from test.AcmeMegastoreTestCase import AcmeMegastoreTestCase


class PopularTestCase(AcmeMegastoreTestCase):
    """
    To work out the "Popular purchases":

    * fetch 5 recent purchases for the user:
      GET /api/purchases/by_user/:username?limit=5
    * for each of those products, get a list of all people who previously
      purchased that product: GET /api/purchases/by_product/:product_id
    * at the same time, request info about the products:
      GET /api/products/:product_id
    * finally, put all of the data together and sort it so that the product
      with the highest number of recent purchases is first.
    """

    @unittest_run_loop
    async def test_popular(self):
        # Use fixture data for realistic testing.
        purchases_by_user = fixtures.purchases_by_user()
        purchases_by_product = fixtures.purchases_by_product()
        products = fixtures.products()

        self.api.purchases_by_user = CoroutineMock()
        self.api.purchases_by_product = CoroutineMock()
        self.api.products = CoroutineMock()
        self.api.purchases_by_user.return_value = purchases_by_user
        self.api.purchases_by_product.side_effect = purchases_by_product
        self.api.products.side_effect = products

        self.popular = Popular(self.api, self.loop)

        user = 'some_user'
        popular = await self.popular.popular(user)

        self.api.purchases_by_user.assert_called_with({'limit': 5},
                                                      username=user)

        # Keep track of each call to the two necessary API methods.
        purchase_calls = []
        products_calls = []

        for purchase in purchases_by_user['purchases']:
            kall = call(product_id=purchase['product_id'])

            if kall in purchase_calls:
                continue

            purchase_calls.append(kall)
            products_calls.append(kall)

        pop_count = len(popular)

        # Make sure the two API methods were called with right arguments and
        # the right number of times (no repeated calls for repeated products).
        # Since we called the two API methods above for each unique product,
        # the number of calls is also the number of popular products we should
        # have received, so we can use that for testing that we got the right
        # number of results.
        self.api.purchases_by_product.assert_has_calls(purchase_calls,
                                                       any_order=True)
        self.api.products.assert_has_calls(products_calls, any_order=True)
        self.assertEqual(self.api.purchases_by_product.call_count, pop_count)
        self.assertEqual(self.api.products.call_count, pop_count)

        # The following assertions are meant to verify if the obtained data
        # is correct. It is not a thorough verification, is highly dependent on
        # the fixture data and assumes a few things about the results, meaning
        # that if the fixture data changes, the assertions will probably need
        # to be changed as well.
        # By the way, assertCountEqual()'s name is a bit misleading. From
        # the docs: a and b have the same elements in the same number,
        # regardless of their order.
        self.assertEqual(popular[0]['id'], 881201)
        self.assertCountEqual(popular[0]['recent'], ['Morgan_Barton',
                                                     'Rodrigo91',
                                                     'Adalberto_Hamill',
                                                     'London.Keebler'])

        self.assertEqual(popular[1]['id'], 96195)
        self.assertCountEqual(popular[1]['recent'], ['Morgan_Barton',
                                                     'London.Keebler',
                                                     'Aida_Conroy71'])

        self.assertEqual(popular[3]['id'], 278646)
        self.assertCountEqual(popular[3]['recent'], ['Morgan_Barton',
                                                     'Zula.Kilback',
                                                     'Gina_Kautzer'])

        self.assertEqual(popular[2]['id'], 187478)
        self.assertCountEqual(popular[2]['recent'], ['Morgan_Barton',
                                                     'Zula.Kilback',
                                                     'Adalberto_Hamill'])

        self.assertEqual(popular[5]['id'], 469837)
        self.assertCountEqual(popular[5]['recent'],
                              ['Morgan_Barton', 'Felicia44'])

        self.assertEqual(popular[4]['id'], 637806)
        self.assertCountEqual(popular[4]['recent'],
                              ['Morgan_Barton', 'Felicia44'])

        self.assertEqual(popular[6]['id'], 380117)
        self.assertCountEqual(popular[6]['recent'], ['Morgan_Barton'])
