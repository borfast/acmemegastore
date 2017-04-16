# coding=utf-8
import os
from random import uniform as random_uniform
from time import sleep

from flask import Flask, request, jsonify, json, abort

app = Flask(__name__)

# Ugly global object but injecting it into the Flask app would require extra
# work that isn't worth it for the purpose of this tiny piece of the demo.
# Besides, dependency injection has already been demonstrated on the main
# server.
data = {}


def load_data():
    path = os.path.realpath(os.path.dirname(__file__))
    path = os.path.join(path, 'data.json')
    with open(path) as fp:
        result = json.load(fp)

    return result


def get_all_items_by_key(key):
    """ DRY function to get a full list of items given that list's key. """
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))
    return data[key][skip:skip+limit-1]


def get_items_by_filter(data_key, comparison_key, comparison_data):
    """ DRY function to filter items from a list. """
    return list(filter(lambda x: x[comparison_key] == comparison_data,
                       data[data_key]))


def get_purchases(purchases):
    """ Generic DRY function to respond to requests for purchases. """
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 10))

    if len(purchases) > 0:
        return jsonify({'purchases': purchases[skip:skip + limit - 1]})
    else:
        abort(404)


@app.route('/api/products')
def products():
    return jsonify({'products': get_all_items_by_key('products')})


@app.route('/api/products/<int:product_id>')
def product(product_id):
    p = get_items_by_filter('products', 'id', product_id)

    if len(p) > 0:
        return jsonify({'product': p[0]})
    else:
        abort(404)


@app.route('/api/users')
def users():
    return jsonify({'users': get_all_items_by_key('users')})


@app.route('/api/users/<username>')
def user(username):
    u = get_items_by_filter('users', 'username', username)
    if len(u) > 0:
        return jsonify({'user': u[0]})
    else:
        abort(404)


@app.route('/api/purchases/by_user/<username>')
def purchases_by_user(username):
    p = get_items_by_filter('purchases', 'username', username)
    return get_purchases(p)


@app.route('/api/purchases/by_product/<int:product_id>')
def purchases_by_product(product_id):
    p = get_items_by_filter('purchases', 'product_id', product_id)
    return get_purchases(p)

if __name__ == "__main__":
    data = load_data()
    app.before_request(lambda: sleep(random_uniform(0.5, 1)))
    app.run(host='0.0.0.0', port=8085)
