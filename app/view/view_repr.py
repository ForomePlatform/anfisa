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

import numbers
from io import StringIO
from html import escape

#===============================================
def htmlEscape(val):
    if val is None:
        return "null"
    if val == "":
        return ""
    return escape(str(val))

#===============================================
def jsonHtmlRepr(obj, level = 0):
    if obj is None:
        return "null"
    if isinstance(obj, str):
        return htmlEscape(obj)
    if isinstance(obj, numbers.Number):
        return str(obj)
    if isinstance(obj, dict):
        if level < 2:
            ret = []
            for key in sorted(obj.keys()):
                if level == 0:
                    ret.append("<b>%s</b>: " % htmlEscape(key))
                    ret.append("<br/>")
                else:
                    ret.append("%s: " % htmlEscape(key))
                rep_val = jsonHtmlRepr(obj[key], level + 1)
                if level == 0:
                    rep_val = htmlEscape(rep_val)
                ret.append(rep_val)
                ret.append(", ")
                if level == 0:
                    ret.append("<br/>")
            while len(ret) > 0 and ret[-1] in ("<br/>", ", "):
                del ret[-1]
            return ''.join(ret)
        return '{' + ', '.join(['%s:"%s"' %
            (key, jsonHtmlRepr(obj[key], level + 1))
            for key in sorted(obj.keys())]) + '}'
    elif isinstance(obj, list):
        ret = '[' + ', '.join([jsonHtmlRepr(sub_obj, level + 1)
            for sub_obj in obj]) + ']'
        if level == 0:
            return htmlEscape(ret)
        return ret
    return '???'

#===============================================
def vcfRepr(vcf_content):
    output = StringIO()
    collect_str = ""
    for fld in vcf_content.split('\t'):
        if len(fld) < 40:
            if len(collect_str) < 60:
                collect_str += "\t" + fld
            else:
                print(collect_str[1:], file = output)
                collect_str = "\t" + fld
            continue
        if collect_str:
            print(collect_str[1:], file = output)
            collect_str = ""
        for vv in fld.split(';'):
            var, q, val = vv.partition('=')
            if var == "CSQ":
                print("==v====SCQ======v========", file = output)
                for idx, dt in enumerate(val.split(',')):
                    ddd = dt.split('|')
                    print("%d:\t%s" % (idx, '|'.join(ddd[:12])), file = output)
                    print("\t|%s" % ('|'.join(ddd[12:29])), file = output)
                    print("\t|%s" % ('|'.join(ddd[28:33])), file = output)
                    print("\t|%s" % ('|'.join(ddd[33:40])), file = output)
                    print("\t|%s" % ('|'.join(ddd[40:50])), file = output)
                    print("\t|%s" % ('|'.join(ddd[50:])), file = output)
                print("==^====SCQ======^========", file = output)
            else:
                print(vv, file = output)
    if collect_str:
        print(collect_str[1:], file = output)
    return output.getvalue()
