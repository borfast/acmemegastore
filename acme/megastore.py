# coding=utf-8
import json
from asyncio import AbstractEventLoop

from aiohttp import web

from .api import Api
from .errors.api import ApiError
from .popular import Popular


class Megastore:
    MSG_USERNAME_NOT_FOUND = "User with username of '{}' was not found"

    def __init__(self, config: dict, api: Api, loop: AbstractEventLoop):
        self.config = config
        self.api = api
        self.loop = loop

    async def recent_purchases(self, request):
        username = request.match_info.get('username', None)

        # First we need to check if we have a valid username.
        # It would be more Pythonic to try to get the popular purchases right
        # away from the API and catch an exception ("better ask for forgiveness
        # than ask for permission") but the data API always responds with
        # 200, even for users that don't exist, so we would still need to
        # call the /users endpoint to see if we have a valid username and
        # that's not the responsibility of the Popular class.
        try:
            user_info = await self.api.user(username=username)
            if 'user' not in user_info:
                response = self.MSG_USERNAME_NOT_FOUND.format(username)
                return web.Response(body=str.encode(response),
                                    content_type='text/plain')
        except ApiError as e:
            return web.Response(body=str.encode(e.__str__()))

        pop = Popular(self.api, self.loop)
        try:
            purchases = await pop.popular(username)
            response = json.dumps(purchases)

            return web.Response(body=str.encode(response),
                                content_type='application/json')
        except ApiError as e:
            return web.Response(body=str.encode(e.__str__()))
