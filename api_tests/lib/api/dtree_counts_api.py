

from lib.api.api_client import ApiRequest

apiRequest = ApiRequest(method='POST', path='dtree_counts')


class DtreeCounts:

    @staticmethod
    def post(parameters):
        return apiRequest.request(parameters)