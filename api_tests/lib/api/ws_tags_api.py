"""
This module contains WsTags requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ws_tags')


class WsTags:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
