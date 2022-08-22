import requests
from lib.config.api_config import ApiConfig

default_headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}


class ApiRequest:
    def __init__(self, path: str, method: str, headers=None):
        if headers is None:
            headers = default_headers
        self._base_url = ApiConfig.base_url
        self._path = path
        self._method = method
        self._headers = headers

    def request(self, params):
        url = self._base_url + self._path
        headers = self._headers
        print('url: ' + url)
        print('params')
        print(params)
        return requests.request(
            method=self._method,
            url=url,
            params=params,
            headers=headers,
        )

    def request_with_formdata(self, payload):
        url = self._base_url + self._path
        print('url: ' + url)
        print('payload')
        print(payload)
        return requests.request(
            method=self._method,
            url=url,
            data=payload,
            files=payload
        )
