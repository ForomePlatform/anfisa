
from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='symbol_info')


class SymbolInfo:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
