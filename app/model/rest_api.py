
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

#===============================================
class RestAPI:
    sRQ_Methods = dict()

    @classmethod
    def _regRequest(cls, func, kind):
        rq_name = func.__name__
        assert rq_name.startswith("rq__")
        rq_name = rq_name[4:]
        assert rq_name not in cls.sRQ_Methods
        cls.sRQ_Methods[rq_name] = (func, kind)
        return func

    @classmethod
    def vault_request(cls, func):
        return cls._regRequest(func, "vault")

    @classmethod
    def ws_request(cls, func):
        return cls._regRequest(func, "ws")

    @classmethod
    def xl_request(cls, func):
        return cls._regRequest(func, "xl")

    @classmethod
    def lookupRequest(cls, rq_path, rq_args, data_vault):
        if rq_path.startswith('/'):
            rq_info = cls.sRQ_Methods.get(rq_path[1:])
            if rq_info is not None:
                rq_func, rq_kind = rq_info
                if rq_kind == "vault":
                    return (rq_func, data_vault)
                elif rq_kind == "ws":
                    ws_h = data_vault.getWS(rq_args.get("ws"))
                    if ws_h is not None:
                        return (rq_func, ws_h)
                else:
                    assert rq_kind == "xl"
                    ds_h = data_vault.getXL(rq_args.get("ds"))
                    if ds_h is not None:
                        return (rq_func, ds_h)
        return None, None
