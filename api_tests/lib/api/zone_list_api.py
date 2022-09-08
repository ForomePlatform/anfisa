"""
This module contains Zone_list requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='zone_list')


class ZoneList:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
