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
import logging, re, json
import bson.json_util as bjs

def toJSON(bobj):
    return json.loads(bjs.dumps(bobj))

#===============================================
class GenesDB:
    def __init__(self, mongo_conn):
        self.mDB_h = mongo_conn.getDB("GeneDb")
        self.mAllSymbols = set()
        self.mActiveSymbols = set()
        self.mMetaInfo = None
        for rec in self.mDB_h["meta"].find():
            assert self.mMetaInfo is None
            self.mMetaInfo = toJSON(rec)["meta"]
        for rec in self.mDB_h["symbols"].find():
            symb = rec["_id"]
            if "gtf" in rec:
                self.mActiveSymbols.add(symb)
            self.mAllSymbols.add(symb)
        logging.info(f"GeneDb started with {len(self.mAllSymbols)} records, "
            + str(self.mMetaInfo))

    def getAllSymbols(self):
        return self.mAllSymbols

    def getMetaInfo(self):
        return self.mMetaInfo

    def getSymbolInfo(self, symbol_name, extra = None):
        if symbol_name not in self.mAllSymbols:
            if extra and symbol_name in extra:
                return {
                    "_id": symbol_name,
                    "gtf": [{"-": "no information provided"}]}
            return None
        ret = self.mDB_h["symbols"].find_one({"_id": symbol_name})
        return toJSON(ret)

    def selectSymbols(self, pattern, active_only = False,
            gene_list = None, extra = None):
        if len(pattern) < 3 or sum(chr.isalnum() for chr in pattern) < 2:
            return None
        patt = re.compile(
            '^' + pattern.replace('*', '.*') + '$', re.IGNORECASE)
        ret = set()
        symbol_names = self.mActiveSymbols if active_only else self.mAllSymbols
        if extra is not None:
            symbol_names = symbol_names | extra
        if gene_list:
            symbol_names &= set(gene_list)
        for symbol_name in symbol_names:
            if patt.match(symbol_name):
                ret.add(symbol_name)
        return sorted(ret)
