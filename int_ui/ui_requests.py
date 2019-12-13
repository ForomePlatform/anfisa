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

from utils.log_err import logException
from .gen_html import formWsPage, noRecords, dirPage, notFound
from .html_xl import formXLPage
from .html_dtree import formDTreePage
from .record import reportWsRecord, reportDsRecord
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
            workspace = data_vault.getDS(rq_args["ds"], "ws")
            if workspace is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formWsPage(output, cls.sHtmlTitle, cls.sHtmlBase,
                workspace, cls.sWsPubURL)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/rec":
            workspace = data_vault.getDS(rq_args["ds"], "ws")
            rec_no = int(rq_args.get("rec"))
            if workspace:
                output = StringIO()
                reportWsRecord(output, workspace, rec_no,
                    rq_args.get("details"), rq_args.get("port"))
                return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/ds_rec":
            dataset = data_vault.getDS(rq_args["ds"])
            rec_no = int(rq_args.get("rec"))
            if dataset:
                output = StringIO()
                reportDsRecord(output, dataset, rec_no)
                return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/dir":
            output = StringIO()
            dirPage(output, cls.sHtmlTitle, cls.sHtmlBase, cls.sWsPubURL)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/norecords":
            output = StringIO()
            noRecords(output)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/xl_flt":
            xl_ds = data_vault.getDS(rq_args["ds"], "xl")
            if xl_ds is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formXLPage(output, cls.sHtmlTitle, cls.sHtmlBase,
                xl_ds, cls.sWsPubURL)
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
            dataset = data_vault.getDS(rq_args["ds"])
            if dataset:
                output = StringIO()
                formDocNavigationPage(output,
                    cls.sHtmlTitle, cls.sHtmlBase, dataset)
                return serv_h.makeResponse(content = output.getvalue())

        logging.error("BAD server request: " + rq_path)
        return cls.notFoundResponse(serv_h)
