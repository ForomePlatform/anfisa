

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='export')


class Export:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)