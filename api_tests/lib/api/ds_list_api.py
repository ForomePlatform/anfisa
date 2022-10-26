"""
This module contains DsList requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ds_list')


class DsList:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)

