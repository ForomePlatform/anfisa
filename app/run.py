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

import sys, logging
import logging.config
from pythonjsonlogger import jsonlogger

from forome_tools.json_conf import loadJSonConfig
from forome_tools.hserv import setupHServer, HServHandler
from app.top.a_app import AnfisaApp
#========================================
import forome_tools
forome_tools.compatible((0, 1, 9))

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
        def log_message(self, format_str, *args):
            logging.info(("%s - - [%s] %s\n" %
                (self.client_address[0], self.log_date_time_string(),
                format_str % args)).rstrip())

    #========================================
    app_config = loadJSonConfig(config_file,
        home_base_file = __file__, home_base_level = 1)
    host, port = setupHServer(AnfisaApp, app_config, in_container = False)
    httpd = make_server(host, port, application,
        handler_class = _LoggingWSGIRequestHandler)
    print("HServer listening %s:%d" % (host, port), file = sys.stderr)
    httpd.serve_forever()
else:
    logging.basicConfig(level = 10)
    app_config = loadJSonConfig("./anfisa.json",
        home_base_file = __file__, home_base_level = 1)
    setupHServer(AnfisaApp, app_config, in_container = True)
