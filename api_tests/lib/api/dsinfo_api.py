"""
This module Dsinfo get request
"""
from lib.api.api_client import ApiRequest
apiRequest = ApiRequest(method='GET', path='dsinfo?')


class Dsinfo:

    @staticmethod
    def get(parameters, success=True):
        response = apiRequest.request(parameters)
        if success:
            assert response.status_code == 200
            # pprint(response.json())
        else:
            assert response.status_code == 403
            # print(response.text)
        return response
