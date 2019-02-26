import argparse
import json
from collections import namedtuple

import requests


def json2obj(data):
    # Parse JSON into an object with attributes corresponding to dict keys.
    return json.loads(data, object_hook=lambda d: namedtuple('JsonData', d.keys())(*d.values()))


def get(url):
    """
    HTTP GET request
    :param url: - api url
    :return: - json object, if response status is OK
    """
    response = requests.get(url)
    if response.status_code == 200:
        return json2obj(response.text)

    raise Exception(response.text)


def getJson(url):
    """
    HTTP GET request
    :param url: - api url
    :return: - json object, if response status is OK
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.text

    raise Exception(response.text)


def normalize_ref(ref):
    ref = ref.upper()
    if (ref == "GRCH37"):
        return "HG19"
    if (ref == "GRCH38"):
        return "HG38"
    return ref


class Beacon:
    """
   Beacon Network API
   Endpoints:
        /beacons	Lists beacons
        /beacons/{beacon}
        /organizations
        /organizations/{organization}
        /responses	Queries beacons.	Go to example
        /responses/{beacon}	Queries a beacon.	Go to example
        /chromosomes	Lists supported chromosome.	Go to example
        /alleles	Lists supported alleles.	Go to example
        /references	Lists supported reference genomes.	Go to example
   """
    BASE_URL = "https://beacon-network.org/"
    SEARCH_URI = "#/search?pos={pos}&chrom={chromosome}&allele={alt}&ref={ref}&rs=GRCh37"
    PUBLIC_URL = "{}{}".format(BASE_URL,SEARCH_URI)

    def __init__(self, baseUrl=None, resJson=False, beacon = None):
        if (not baseUrl):
            baseUrl = self.BASE_URL
        self.baseUrl = baseUrl + "api"
        self.resJson = resJson
        if (beacon):
            self.beacon_list = [beacon]
        else:
            self.beacon_list = self.getIds(self.beaconList())
        self.beacons_by_ref = dict()
        for beacon in self.beacon_list:
            info = self.beacon(beacon)
            if (info.aggregator):
                continue
            refs = info.supportedReferences
            for ref in refs:
                ref = ref.upper()
                if not ref in self.beacons_by_ref:
                    self.beacons_by_ref[ref] = []
                self.beacons_by_ref[ref].append(beacon)
            pass

    def search(self, chrom, pos, allele, ref):
        """
        /search?pos=32936732&chrom=13&allele=C&ref=G&rs=GRCh37
        :return:
        """
        ref = normalize_ref(ref)
        if (not ref in self.beacons_by_ref):
            raise Exception("Given Beacons do not support reference: {}".format(ref))
        beacon = self.beacons_by_ref[ref]
        if self.resJson:
            return self.responsesJson(chrom, pos, allele, ref, beacon)
        else:
            return self.responses(chrom, pos, allele, ref, beacon)

    def search_individually(self, chrom, pos, allele, ref):
        """
        /search?pos=32936732&chrom=13&allele=C&ref=GRCh37
        :return:
        """
        ref = normalize_ref(ref)
        if (not ref in self.beacons_by_ref):
            raise Exception("Given Beacons do not support reference: {}".format(ref))
        responses = []
        for beacon in self.beacons_by_ref[ref]:
            try:
                response = self.responsesBeacon(chrom, pos, allele, ref, beacon)
                responses.append(response)
                print "{}: {}".format(response.response, beacon)
            except:
                print "ERROR: {}".format(beacon)
                pass
        return responses

    def beaconList(self):
        return get(self.baseUrl + "/beacons")

    def beacon(self, beacon):
        return get(self.baseUrl + "/beacons/" + beacon)

    def organizationList(self):
        return get(self.baseUrl + "/organizations")

    def organization(self, org):
        return get(self.baseUrl + "/organizations/" + org)

    def chromosomes(self):
        return get(self.baseUrl + "/chromosomes")

    def alleles(self):
        return get(self.baseUrl + "/alleles")

    def references(self):
        return get(self.baseUrl + "/references")

    def responses(self, chrom, pos, allele, ref, beacon):
        """
        :param chrom: Chromosome ID. Accepted values: 1-22, X, Y, MT.
                    Note: For compatibility with conventions set by some of the existing beacons,
                          an arbitrary prefix is accepted as well (e.g. chr1 is equivalent to chrom1 and 1).
        :param pos: Coordinate within a chromosome. Position is a number and is 0-based.
        :param allele: Any string of nucleotides A,C,T,G or D, I for deletion and insertion, respectively.
                    Note: For compatibility with conventions set by some of the existing beacons,
                          DEL and INS identifiers are also accepted.
        :param ref: Genome ID. If not specified, all the genomes supported by the given beacons are queried.
                    Note: For compatibility with conventions set by some of the existing beacons,
                          both GRC or HG notation are accepted, case insensitive.
                    Optional parameter.
        :param beacons: Beacon IDs. If specified, only beacons with the given IDs are queried.
                    Responses from all the supported beacons are obtained otherwise.
                    Format: [id1,id2].
                    Optional parameter.
        """
        # https://beacon-network.org/api/responses?chrom=17&pos=41244981&allele=G&ref=GRCh37&beacon=[amplab,brca-exchange]
        param = self.__responsesParam(chrom, pos, allele, ref, beacon)
        return get(self.baseUrl + "/responses" + param)

    def __responsesParam(self, chrom, pos, allele, ref, beacon):
        return "?chrom={}&pos={}&allele={}&ref={}&beacon=[{}]" \
            .format(chrom, pos, allele, ref, ",".join(beacon))

    def responsesBeacon(self, chrom, pos, allele, ref, beacon):
        """
        params: see responses
        """
        # https://beacon-network.org/api/responses?chrom=17&pos=41244981&allele=G&ref=GRCh37&beacon=[amplab,brca-exchange]
        param = "?chrom={}&pos={}&allele={}&ref={}" \
            .format(chrom, pos, allele, ref)
        return get(self.baseUrl + "/responses/" + beacon + param)

    def responsesJson(self, chrom, pos, allele, ref, beacon):
        param = self.__responsesParam(chrom, pos, allele, ref, beacon)
        return getJson(self.baseUrl + "/responses" + param)

    def getIds(selfs, obj):
        return list(map(lambda o: o.id, obj))

    def beaconToString(self, beacon):
        formatStr = "id: '{}';" + \
                    " name: '{}';" + \
                    " url: '{}';" + \
                    " organization: '{}';" + \
                    " description: '{}';" + \
                    " homePage: '{}';" + \
                    " email: '{}';" + \
                    " aggregator: '{}';" + \
                    " visible: '{}';" + \
                    " enabled: '{}';" + \
                    " supportedReferences: '{}';"
        return formatStr.format(beacon.id,
                                beacon.name,
                                beacon.url,
                                beacon.organization,
                                beacon.description,
                                beacon.homePage,
                                beacon.email,
                                beacon.aggregator,
                                beacon.visible,
                                beacon.enabled,
                                beacon.supportedReferences)

    def orgToString(self, org):
        formatStr = "id: '{}';" + \
                    " name: '{}';" + \
                    " description: '{}';" + \
                    " url: '{}';" + \
                    " address: '{}';" + \
                    " len(logo): '{}';"
        return formatStr.format(org.id,
                                org.name,
                                org.description,
                                org.url,
                                org.address,
                                len(org.logo))


def processing(args):
    beacon = Beacon(args.url__baseUrl, True, args.beacon) if args.url__baseUrl else Beacon(resJson=True, beacon=args.beacon)
    try:
        res = beacon.search(chrom=args.chrom, pos=args.pos, allele=args.allele, ref=args.ref)
        print res
        return
    except:
        print "Exception for all Beacons "

    res = beacon.search_individually(chrom=args.chrom, pos=args.pos, allele=args.allele, ref=args.ref)
    print res


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--chrom", help="Chromosome ID. Accepted values: 1-22, X, Y, MT", required=True)
    parser.add_argument("-p", "--pos", help="Coordinate within a chromosome. Position is a number and is 0-based",
                        required=True)
    parser.add_argument("-a", "--allele",
                        help="Any string of nucleotides A,C,T,G or D, I for deletion and insertion, respectively",
                        required=True)
    parser.add_argument("-r", "--ref",
                        help="Genome ID. If not specified, all the genomes supported by the given beacons are queried.",
                        required=True)
    parser.add_argument("-rs", "--referenceAllele", help="reference allele", required=True)
    parser.add_argument("-url" "--baseUrl", help="base url, default: http://beacon-network.org/")
    parser.add_argument("-b", "--beacon", help="beacon id, if ommited all beacons are used")
    args = parser.parse_args()
    processing(args)
