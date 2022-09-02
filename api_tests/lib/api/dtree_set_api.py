"""
This module contains DtreeSet requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_set')


class DtreeSet:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response