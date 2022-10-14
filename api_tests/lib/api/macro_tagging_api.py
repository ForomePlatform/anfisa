

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='macro_tagging')


class MacroTagging:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)