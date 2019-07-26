import sys, logging
import logging.config

from utils.hserv import setupHServer, HServHandler
from app.top.a_app import AnfisaApp

#========================================
if sys.version_info < (3, 7):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

#========================================
def application(environ, start_response):
    return HServHandler.request(environ, start_response)

#========================================
if __name__ == '__main__':
    logging.basicConfig(level = 0)
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "anfisa.json"

    from wsgiref.simple_server import make_server, WSGIRequestHandler

    #========================================
    class _LoggingWSGIRequestHandler(WSGIRequestHandler):
        def log_message(self, format, *args):
            logging.info(("%s - - [%s] %s\n" %
                (self.client_address[0], self.log_date_time_string(),
                format % args)).rstrip())

    #========================================
    host, port = setupHServer(AnfisaApp, config_file, False)
    httpd = make_server(host, port, application,
        handler_class = _LoggingWSGIRequestHandler)
    print("HServer listening %s:%d" % (host, port), file = sys.stderr)
    httpd.serve_forever()
else:
    logging.basicConfig(level = 10)
    setupHServer(AnfisaApp, "./anfisa.json", True)
