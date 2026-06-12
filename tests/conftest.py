import copy
import asyncio

import pytest
import httpx

from src.app import activities, app


class SyncASGIClient:
    def __init__(self, asgi_app):
        transport = httpx.ASGITransport(app=asgi_app)
        self._client = httpx.AsyncClient(transport=transport, base_url="http://testserver")

    def request(self, method, url, **kwargs):
        return asyncio.run(self._client.request(method, url, **kwargs))

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def close(self):
        asyncio.run(self._client.aclose())


@pytest.fixture
def client():
    test_client = SyncASGIClient(app)
    try:
        yield test_client
    finally:
        test_client.close()


@pytest.fixture(autouse=True)
def reset_activities_state():
    original_activities = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_activities)