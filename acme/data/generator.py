# coding=utf-8
import json
from random import randrange

import arrow
from faker import Factory

from .faces import faces

fake = Factory.create()


def generate_user():
    email = fake.email()
    username = email.split("@")[0]

    return {
        'username': username,
        'email': email
    }


def generate_product():
    return {
        'id': randrange(1, 999999),
        'face': faces[randrange(0, len(faces))],
        'price': randrange(1, 1234),
        'size': randrange(12, 40)
    }


def generate_purchases(users, products, max_purchases_per_user):
    num_products = len(products)

    def generate_purchase(user):
        date = arrow.utcnow().replace(seconds=-randrange(100, 999999))

        return {
            'id': randrange(1, 999999),
            'username': user['username'],
            'product_id': products[randrange(0, num_products)]['id'],
            'date': date.isoformat()
        }

    purchases = []
    n = randrange(0, max_purchases_per_user)
    for user in users:
        purchases.extend([generate_purchase(user) for _ in range(0, n)])

    return purchases

    # return list(map(gen, users))


def generate_data():
    num_users = 10
    num_products = 20
    max_purchases_per_user = 10
    users = [generate_user() for _ in range(0, num_users)]
    products = [generate_product() for _ in range(0, num_products)]
    purchases = generate_purchases(users, products, max_purchases_per_user)

    return {
        'users': users,
        'products': products,
        'purchases': purchases
    }


if __name__ == '__main__':
    print(json.dumps(generate_data()))
