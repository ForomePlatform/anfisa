"""
This module contains Ds2ws requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_check')


class DtreeCheck:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
