"""
This module contains TagSelect requests
"""

from lib.api.api_client import ApiRequest
apiRequest = ApiRequest(method='GET', path='tag_select')


class TagSelect:

    @staticmethod
    def get(parameters):
        return apiRequest.request(parameters)
