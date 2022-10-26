
from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='symbols')


class Symbols:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
