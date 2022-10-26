

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_cmp')


class DtreeCmp:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)