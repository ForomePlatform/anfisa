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

    def call(self, request_data, method = "POST", add_path = ""):
        if request_data is not None:
            content = json.dumps(request_data, ensure_ascii = False)
        else:
            content = ""
        conn = HTTPConnection(self.mHost, self.mPort)
        path = self.mPath + add_path
        conn.request(method, path,
            body = content.encode("utf-8"), headers = self.sHeaders)
        res = conn.getresponse()
        try:
            content = res.read()
            logging.info("REST " + method  + " call: " + self.mName +
                add_path + " response: " + str(res.status) +
                " reason: " + str(res.reason))
            if res.status != 200:
                raise RuntimeError("Druid call failure:\n" +
                    str(content, "utf-8"))
        finally:
            res.close()
        if method == "DELETE":
            return None
        return json.loads(str(content, 'utf-8'))
