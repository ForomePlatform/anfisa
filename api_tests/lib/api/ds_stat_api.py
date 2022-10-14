"""
This module contains DsStat requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ds_stat')


class DsStat:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
