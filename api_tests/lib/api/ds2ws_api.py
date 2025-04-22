"""
This module contains Ds2ws requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='ds2ws')


class Ds2ws:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
