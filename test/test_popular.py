# coding=utf-8
from unittest.mock import call

from acme.popular import Popular

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


async def test_popular(api, loop, purchases_by_user, purchases_by_product,
                       products):
    pop = Popular(api, loop)

    user = 'some_user'
    popular = await pop.popular(user)

    api.purchases_by_user.assert_called_once_with({'limit': 5}, username=user)

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
    api.purchases_by_product.assert_has_calls(purchase_calls, any_order=True)
    api.products.assert_has_calls(products_calls, any_order=True)
    assert api.purchases_by_product.call_count == pop_count
    assert api.products.call_count == pop_count

    # The following assertions are meant to verify if the obtained data
    # is correct. It is not a thorough verification, is highly dependent on
    # the fixture data and assumes a few things about the results, meaning
    # that if the fixture data changes, the assertions will probably need
    # to be changed as well.
    assert popular[0]['id'] == 881201
    assert sorted(popular[0]['recent']) == ['Adalberto_Hamill',
                                            'London.Keebler',
                                            'Morgan_Barton',
                                            'Rodrigo91']
    #
    assert popular[1]['id'] == 96195
    assert sorted(popular[1]['recent']) == ['Aida_Conroy71',
                                            'London.Keebler',
                                            'Morgan_Barton']

    assert popular[2]['id'] == 187478
    assert sorted(popular[2]['recent']) == ['Adalberto_Hamill',
                                            'Morgan_Barton',
                                            'Zula.Kilback']

    assert popular[3]['id'] == 278646
    assert sorted(popular[3]['recent']) == ['Gina_Kautzer',
                                            'Morgan_Barton',
                                            'Zula.Kilback']

    assert popular[4]['id'] == 637806
    assert sorted(popular[4]['recent']) == ['Felicia44', 'Morgan_Barton']

    assert popular[5]['id'] == 469837
    assert sorted(popular[5]['recent']) == ['Felicia44', 'Morgan_Barton']

    assert popular[6]['id'] == 380117
    assert sorted(popular[6]['recent']) == ['Morgan_Barton']
