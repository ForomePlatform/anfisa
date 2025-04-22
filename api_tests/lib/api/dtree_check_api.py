"""
This module contains DtreeCheck requests
"""

from lib.api.api_client import ApiRequest

headers = {'Content-type': 'application/x-www-form-urlencoded', 'Accept': 'text/plain'}
apiRequest = ApiRequest(method='POST', path='dtree_check', headers=headers)


class DtreeCheck:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
