"""
This module contains AdmUpdate requests
"""

from lib.api.api_client import ApiRequest
apiRequest = ApiRequest(method='POST', path='adm_update')


class AdmUpdate:

    @staticmethod
    def post():
        return apiRequest.request()
