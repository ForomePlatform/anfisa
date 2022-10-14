

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='recdata')


class Recdata:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)
