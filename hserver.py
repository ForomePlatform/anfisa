import sys, os, traceback, logging, codecs, cgi, types
from StringIO import StringIO
from lxml     import etree
from urlparse import parse_qs
import logging.config

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn

from app.a_serv import AnfisaService
#===============================================
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

#========================================
sHServer = None
class HServHandler(BaseHTTPRequestHandler):
    sConfig = None

    sContentTypes = {
        "html":   "text/html",
        "xml":    "text/xml",
        "css":    "text/css",
        "js":     "application/javascript",
        "png":     "image/png"}

    sErrorCodes = {
        202: "202 Accepted",
        204: "204 No Content",
        303: "303 See Other",
        400: "400 Bad Request",
        408: "408 Request Timeout",
        404: "404 Not Found",
        422: "422 Unprocessable Entity",
        423: "423 Locked",
        500: "500 Internal Error"}

    def makeResponse(self,
            mode        = "html",
            content     = None,
            error       = None,
            add_headers = None,
            without_decoding = False):
        response_code = 200
        response_status = "200 OK"
        if error is not None:
            response_code = error
            response_status  = self.sErrorCodes[error]
        if content is not None:
            if without_decoding:
                response_body = content
            else:
                response_body = content.encode("utf-8")
            response_headers = [("Content-Type", self.sContentTypes[mode]),
                                ("Content-Length", str(len(response_body)))]
        else:
            response_body = response_status
            response_headers = []
        if add_headers is not None:
            response_headers += add_headers

        self.send_response(response_code, response_status)
        for name, value in response_headers:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(response_body)
        self.wfile.flush()
        return True

    def log_message(self, format, *args):
        logging.info(("%s - - [%s] %s\n" % (self.client_address[0],
            self.log_date_time_string(), format%args)).rstrip())

    def address_string(self):
        host, port = self.client_address[:2]
        #return socket.getfqdn(host)
        return host

    #===============================================
    def parseRequest(self):
        path, q, query_string = self.path.partition('?')

        query_args = dict()
        if query_string:
            for a, v in parse_qs(query_string).items():
                query_args[a] = v[0]

        if self.command == "POST":
            try:
                form = cgi.FieldStorage(fp = self.rfile,
                    headers = self.headers,
                    environ = {'REQUEST_METHOD':'POST',
                    'CONTENT_TYPE':self.headers['Content-Type']})
                for arg in form.keys():
                    val = form[arg]
                    if isinstance(val, types.ListType):
                        val = val[0]
                    query_args[arg] = val.value.decode("utf-8")
            except Exception:
                rep = StringIO()
                traceback.print_exc(file = rep)
                log_record = rep.getvalue()
                logging.error(
                    "Exception on read request body:\n " + log_record)

        return path, query_args

    #===============================================
    def fileResponse(self, fname,  without_decoding):
        fpath = self.sConfig["files"] + fname
        if not os.path.exists(fpath):
            return False
        if without_decoding:
            inp = open(fpath, "r")
            content = inp.read()
        else:
            with codecs.open(fpath, "r", encoding = "utf-8") as inp:
                content = inp.read()
        inp.close()
        return self.makeResponse(mode = fname.rpartition('.')[2],
            content = content,  without_decoding = without_decoding)

    #===============================================
    def do_GET(self):
        global sHServer
        try:
            path, query_args = self.parseRequest()
            print(path, query_args)
            if path.find('.') != -1:
                ret = self.fileResponse(path, True)
                if ret is not False:
                    return ret
            return AnfisaService.request(self, path, query_args)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep)
            log_record = rep.getvalue()
            logging.error(
                "Exception on GET request:\n " + log_record)
            return self.makeResponse(error = 500)

    def do_POST(self):
        return self.do_GET()

#========================================
def runHServer(config_file):
    global sHServer
    if not os.path.exists(config_file):
        logging.critical("No config file provided (hserv.xml)")
        sys.exit(2)
    config = dict()
    with open(config_file) as inp:
        cfg_tree = etree.parse(inp, etree.XMLParser())
        config["version"] = cfg_tree.xpath("/conf")[0].get("version")
        for nd in cfg_tree.xpath("/conf/*"):
            value = nd.text.strip() if nd.text else ""
            if nd.tag in config:
                logging.critical("Config: duplicate property %s" % nd.tag)
                sys.exit(1)
            config[nd.tag] = value
    HServHandler.sConfig = config
    AnfisaService.start(cfg_tree)
    host, port = config["host"], int(config["port"])
    server = ThreadedHTTPServer((host, port), HServHandler)
    logging.info("HServer listening %s:%d" % (host, port))
    server.serve_forever()

#========================================
if __name__ == '__main__':
    logging.basicConfig(level = 10)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "anfisa.xml"
    runHServer(config_file)
