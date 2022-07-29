import requests
import os
from pathlib import Path
from dotenv import load_dotenv
config_dir = Path(__file__).parent.parent.parent
dotenv_file = config_dir / f'.env'

load_dotenv(dotenv_file)
BASE_URL = os.environ.get("BASE_URL")


class ApiRequest:
    def __init__(self, path: str, method: str):
        self._path = path
        self._method = method

    def request(self, params):
        url = BASE_URL + self._path
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        print(url)
        print(params)
        return requests.request(
            method=self._method,
            url=url,
            params=params,
            headers=headers,
        )



