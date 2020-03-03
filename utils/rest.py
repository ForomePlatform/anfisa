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

import json, logging
from urllib.parse import urlsplit
from http.client import HTTPConnection

#==================================
class RestAgent:
    sHeaders = {
        "Content-Type": "application/json",
        "Encoding": "utf-8"}

    def __init__(self, url, name = None):
        url_info = urlsplit(url)
        assert url_info.scheme == "http"
        self.mHost = url_info.hostname
        self.mPort = url_info.port
        self.mPath = url_info.path
        if self.mPort is None:
            self.mPort = 80
        self.mName = name if name else url

    def call(self, request_data, method = "POST",
            add_path = "", json_rq_mode = True):
        if request_data is not None:
            if json_rq_mode:
                content = json.dumps(request_data, ensure_ascii = False)
            else:
                content = request_data
                print("C:", request_data)
        else:
            content = ""
        conn = HTTPConnection(self.mHost, self.mPort)
        path = self.mPath + add_path
        conn.request(method, path,
            body = content.encode("utf-8"), headers = self.sHeaders)
        res = conn.getresponse()
        try:
            content = res.read()
            logging.info("REST " + method  + " call: " + self.mName + " "
                + add_path + " response: " + str(res.status)
                + " reason: " + str(res.reason))
            if res.status != 200:
                raise RuntimeError(("Rest call failure (%r):\n" % res.status)
                    + str(content, "utf-8") + '\n========')
        finally:
            res.close()
        if method == "DELETE":
            return None
        return json.loads(str(content, 'utf-8'))
