# coding=utf-8
import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def get_config():
    return {
        'ACME_DEBUG': os.environ.get('ACME_DEBUG', False),
        'API_BASE_URL': os.environ['API_BASE_URL'],
        'CACHE_EXPIRATION': int(os.environ['CACHE_EXPIRATION']),
        'REDIS_HOST': os.environ['REDIS_HOST'],
        'REDIS_PORT': int(os.environ['REDIS_PORT']),
        'REDIS_DB': int(os.environ['REDIS_DB'])
    }
