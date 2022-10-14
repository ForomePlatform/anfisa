"""
This module contains WsList requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ws_list')


class WsList:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
