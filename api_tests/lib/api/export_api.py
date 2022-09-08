

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='export')


class Export:

    @staticmethod
    def post(parameters):
        response = apiRequest.request(parameters)
        print('responseCode:' + str(response.status_code))
        print('responseBody:', response.text)
        return response