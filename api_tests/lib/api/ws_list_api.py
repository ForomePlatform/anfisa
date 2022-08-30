"""
This module contains WsList requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ws_list')


class WsList:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
