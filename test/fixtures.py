# coding=utf-8
import json
import os


def purchases_by_user():
    return _load_json('purchases_by_user.json')


def purchases_by_product():
    return _load_json('purchases_by_product.json')


def products():
    return _load_json('products.json')


def _load_json(filename):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'fixtures', filename)
    with open(path) as fp:
        return json.load(fp)
