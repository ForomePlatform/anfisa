import sys, os, traceback, logging
from io import StringIO
from urllib.parse import parse_qs
from cgi import parse_header, parse_multipart
import logging.config

from .json_conf import loadJSonConfig
#========================================
class HServResponse:
    #========================================
    sContentTypes = {
        "html":   "text/html",
        "xml":    "text/xml",
        "css":    "text/css",
        "js":     "application/javascript",
        "png":    "image/png",
        "json":   "application/json",
        "xlsx":   (
            "application/application/"
            "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }

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

    def __init__(self, start_response):
        self.mStartResponse = start_response

    def makeResponse(self, mode = "html", content = None, error = None,
            add_headers = None, without_decoding = False):
        response_status = "200 OK"
        if error is not None:
            response_status = self.sErrorCodes[error]
        if content is not None:
            if without_decoding:
                response_body = bytes(content)
            else:
                response_body = content.encode("utf-8")
            response_headers = [("Content-Type", self.sContentTypes[mode]),
                                ("Content-Length", str(len(response_body)))]
        else:
            response_body = response_status.encode("utf-8")
            response_headers = []
        if add_headers is not None:
            response_headers += add_headers
        self.mStartResponse(response_status, response_headers)
        return [response_body]

#========================================
class HServHandler:
    sInstance = None

    @classmethod
    def init(cls, application, config, in_container):
        cls.sInstance = cls(application, config, in_container)

    @classmethod
    def request(cls, environ, start_response):
        return cls.sInstance.processRq(environ, start_response)

    def __init__(self, application, config, in_container):
        self.mApplication = application
        self.mDirFiles = config["dir-files"]
        self.mHtmlBase = (config["html-base"]
            if in_container else None)
        if self.mHtmlBase and self.mHtmlBase.endswith('/'):
            self.mHtmlBase = self.mHtmlBase[:-1]
        self.mApplication.setup(config, in_container)

    def checkFilePath(self, path):
        alt_path = self.mApplication.checkFilePath(path)
        if alt_path is not None:
            return alt_path
        for path_from, path_to in self.mDirFiles:
            if path.startswith(path_from):
                return path_to + path[len(path_from):]
        return None

    #===============================================
    def parseRequest(self, environ):
        path = environ["PATH_INFO"]
        if self.mHtmlBase and path.startswith(self.mHtmlBase):
            path = path[len(self.mHtmlBase):]
        if not path:
            path = "/"
        query_string = environ["QUERY_STRING"]

        query_args = dict()
        if query_string:
            for a, v in parse_qs(query_string).items():
                query_args[a] = v[0]

        if environ["REQUEST_METHOD"] == "POST":
            try:
                content_type = environ.get('CONTENT_TYPE')
                if content_type:
                    ctype, pdict = parse_header(content_type)
                    if ctype == 'multipart/form-data':
                        for a, v in parse_multipart(environ['wsgi.input'], pdict).items():
                            print ("a=", a,"v=", v)
                            query_args[a] = v[0]
                    elif ctype != 'application/x-www-form-urlencoded':
                        logging.error("Bad content type for POST: " + ctype)
                    else:
                        content_type = None
                if not content_type:
                    rq_body_size = int(environ.get('CONTENT_LENGTH', 0))
                    rq_body = environ['wsgi.input'].read(rq_body_size)
                    for a, v in parse_qs(rq_body.decode("utf-8")).items():
                        query_args[a] = v[0]
            except Exception:
                rep = StringIO()
                traceback.print_exc(file = rep)
                log_record = rep.getvalue()
                logging.error(
                    "Exception on read request body:\n " + log_record)

        return path, query_args

    #===============================================
    def fileResponse(self, resp_h, fpath,
            query_args, without_decoding):
        if not os.path.exists(fpath):
            return False
        if without_decoding:
            inp = open(fpath, "rb")
            content = inp.read()
        else:
            with open(fpath, "r", encoding = "utf-8") as inp:
                content = inp.read()
        inp.close()

        file_ext  = fpath.rpartition('.')[2]
        add_headers = None

        if file_ext == ".xslx":
            add_headers = [("content-disposition",
                "attachment; filename=%s" %
                query_args.get("disp", fpath.rpartition('/')[2]))]

        return resp_h.makeResponse(mode = file_ext,
            content = content, add_headers = add_headers,
            without_decoding = without_decoding)

    #===============================================
    def processRq(self, environ, start_response):
        resp_h = HServResponse(start_response)
        rq_descr = []
        try:
            path, query_args = self.parseRequest(environ)
            file_path = self.checkFilePath(path)
            if file_path is not None:
                ret = self.fileResponse(resp_h,
                    file_path, query_args, True)
                if ret is not False:
                    return ret
            return self.mApplication.request(
                resp_h, path, query_args, rq_descr)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep, limit = 20)
            log_record = rep.getvalue()
            log_context = ""
            if rq_descr:
                log_context = "In context: " + " ".join(rq_descr) + "\n"
            logging.error("Exception on request evaluation:\n " +
                log_context + log_record)
            return resp_h.makeResponse(error = 500)

#========================================
def setupHServer(application, config_file, in_container):
    if not os.path.exists(config_file):
        logging.critical("No config file provided (%s)" % config_file)
        sys.exit(2)
    config = loadJSonConfig(config_file)
    logging_config = config.get("logging")
    if logging_config:
        logging.config.dictConfig(logging_config)
        logging.basicConfig(level = 0)
    HServHandler.init(application, config, in_container)
    if not in_container:
        return (config["host"], int(config["port"]))
    return None

