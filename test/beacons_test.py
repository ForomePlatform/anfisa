#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import unittest

from beacons.beacon import Beacon


class ExcelExportTest(unittest.TestCase):

    def test_search(self):
        """
        http://beacon-network.org/#/search?pos=32936732&chrom=13&allele=C&ref=G&rs=GRCh37
        :return:
        """
        beacon = Beacon()
        res = beacon.search(chrom=13, pos=32936732, allele='C', ref='G')
        print res
        self.assertTrue(len(res) > 0)

    def test_beacons_list(self):
        """
        List beacons: GET  /beacons
        """
        beacons = Beacon()
        res = beacons.beaconList()
        for b in res:
            print beacons.beaconToString(b)

        self.assertTrue(len(res) > 0)
        self.assertTrue(len(res[0].name) > 0)

    def test_beacon_get(self):
        """
        Shows a beacon: GET /beacons/{beacon}
        """
        beacons = Beacon()
        res = beacons.beacon("amplab")
        print beacons.beaconToString(res)
        self.assertTrue(len(res.name) > 0)

    def test_org_list(self):
        """
        Lists organizations: GET /organizations
        """
        beacons = Beacon()
        res = beacons.organizationList()
        for org in res:
            print beacons.orgToString(org)
        self.assertTrue(len(res) > 0)
        self.assertTrue(len(res[0].name) > 0)

    def test_org_get(self):
        """
        Shows an organization: GET /organizations/{organization}
        """
        beacons = Beacon()
        res = beacons.organization("agha")
        print beacons.orgToString(res)
        self.assertTrue(len(res.name) > 0)

    def test_chromosomes(self):
        """
        List chromosomes: GET /chromosomes
        """
        beacons = Beacon()
        res = beacons.chromosomes()
        print res
        self.assertTrue(len(res) > 0)

    def test_alleles(self):
        """
        List alleles: GET /alleles
        """
        beacons = Beacon()
        res = beacons.alleles()
        print res
        self.assertTrue(len(res) > 0)

    def test_references(self):
        """
        List references: GET /references
        """
        beacons = Beacon()
        res = beacons.references()
        print res
        self.assertTrue(len(res) > 0)

    def test_references(self):
        """
        Queries beacons: GET /responses
        https://beacon-network.org/api/responses?chrom=17&pos=41244981&allele=G&ref=GRCh37&beacon=[amplab,brca-exchange]
        """
        beacons = Beacon()
        res = beacons.responses(chrom=17, pos=41244981, allele='G', ref='GRCh37', beacon=["amplab", "brca-exchange"])
        print res
        self.assertTrue(len(res) > 0)

    def test_referencesBeacon(self):
        """
        Queries beacons: GET /responses/{beacon}
        https://beacon-network.org/api/responses/brca-exchange?chrom=17&pos=41244981&allele=G&ref=GRCh37
        """
        beacons = Beacon()
        res = beacons.responsesBeacon(chrom=17, pos=41244981, allele='G', ref='GRCh37', beacon="brca-exchange")
        print res
        self.assertTrue(len(res) > 0)


if __name__ == '__main__':
    unittest.main()
