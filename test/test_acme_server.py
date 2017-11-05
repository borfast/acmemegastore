# coding=utf-8


async def test_no_username(test_client, app):
    client = await test_client(app)
    resp = await client.get('/')
    assert resp.status == 404
