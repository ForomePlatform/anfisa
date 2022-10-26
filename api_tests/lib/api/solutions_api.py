

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='solutions')


class Solutions:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)