"""
This module Dsinfo get request
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='GET', path='dsinfo?')


class Dsinfo:

    @staticmethod
    def get(parameters):
        return apiRequest.request(parameters)
