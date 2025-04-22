"""
This module contains CsvExport requests
"""
from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='csv_export')


class CsvExport:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
