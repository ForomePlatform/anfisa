"""
This module contains StatUnits requests
"""

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='statunits')


class StatUnits:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
