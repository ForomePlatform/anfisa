"""
This module contains TagSelect requests
"""

from lib.api.api_client import ApiRequest
apiRequest = ApiRequest(method='GET', path='tag_select')


class TagSelect:

    @staticmethod
    def get(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response
