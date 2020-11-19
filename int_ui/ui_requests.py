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

import logging
from io import StringIO

from forome_tools.log_err import logException
from .html_pages import noRecords, dirPage, subdirPage, notFound
from .html_ws import formWsPage
from .html_xl import formXLPage
from .html_dtree import formDTreePage
from .record import reportRecord
from .doc_nav import formDocNavigationPage
#===============================================
class IntUI:
    sHtmlBase = None
    sHtmlTitle = None
    sWsPubURL = None

    @classmethod
    def setup(cls, config, in_container):
        cls.sHtmlTitle = config["html-title"]
        cls.sWsPubURL = config.get("html-ws-url", "ws")
        cls.sHtmlBase = (config["html-base"]
            if in_container else None)
        if cls.sHtmlBase and not cls.sHtmlBase.endswith('/'):
            cls.sHtmlBase += '/'

    @classmethod
    def notFoundResponse(cls, serv_h):
        output = StringIO()
        notFound(output, cls.sHtmlTitle,
            cls.sHtmlBase if cls.sHtmlBase else '/')
        return serv_h.makeResponse(content = output.getvalue(),
            error = 404)

    @classmethod
    def finishRequest(cls, serv_h, rq_path, rq_args, data_vault):
        try:
            return cls._finishRequest(serv_h, rq_path, rq_args, data_vault)
        except Exception:
            logException("Exception on evaluation request")
        return cls.notFoundResponse(serv_h)

    @classmethod
    def _finishRequest(cls, serv_h, rq_path, rq_args, data_vault):
        if rq_path == "/ws":
            ds_h = data_vault.getDS(rq_args["ds"], "ws")
            if ds_h is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formWsPage(output, cls.sHtmlTitle, cls.sHtmlBase,
                ds_h, cls.sWsPubURL)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/rec":
            ds_h = data_vault.getDS(rq_args["ds"])
            if ds_h is None:
                return cls.notFoundResponse(serv_h)
            rec_no = int(rq_args.get("rec"))
            output = StringIO()
            reportRecord(output, ds_h, rec_no, rq_args.get("details"),
                rq_args.get("samples"), int(rq_args.get("port", -1)))
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/dir":
            output = StringIO()
            dirPage(output, cls.sHtmlTitle, cls.sHtmlBase, cls.sWsPubURL,
                data_vault.getApp().getDocSets())
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/subdir":
            ds_h = data_vault.getDS(rq_args["ds"])
            if ds_h is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            subdirPage(output, cls.sHtmlTitle,
                cls.sHtmlBase, cls.sWsPubURL, ds_h)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/norecords":
            output = StringIO()
            noRecords(output)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/xl_flt":
            ds_h = data_vault.getDS(rq_args["ds"], "xl")
            if ds_h is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formXLPage(output, cls.sHtmlTitle, cls.sHtmlBase,
                ds_h, cls.sWsPubURL)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/dtree":
            ds_h = data_vault.getDS(rq_args["ds"])
            if ds_h is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formDTreePage(output, cls.sHtmlTitle,
                cls.sHtmlBase, ds_h, cls.sWsPubURL)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/doc_nav":
            ds_h = data_vault.getDS(rq_args["ds"])
            if ds_h:
                output = StringIO()
                formDocNavigationPage(output,
                    cls.sHtmlTitle, cls.sHtmlBase, ds_h)
                return serv_h.makeResponse(content = output.getvalue())

        logging.error("BAD server request: " + rq_path)
        return cls.notFoundResponse(serv_h)
