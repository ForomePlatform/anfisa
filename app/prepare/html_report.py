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

from datetime import datetime, timedelta
from xml.sax.saxutils import escape

#===============================================
def startHtmlReport(output, title = None, use_pygments = False):
    print('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">''',
    file = output)
    if title:
        print('    <title>%s</title>' % escape(title), file = output)
    print('    <link rel="stylesheet" href="report.css" '
        'type="text/css" media="all"/>', file = output)
    if use_pygments:
        print('    <link rel="stylesheet" href="py_pygments.css" '
            'type="text/css" media="all"/>', file = output)

    print('  </head>', file = output)

#===============================================
def reprDateVal(val):
    if val is None:
        return None
    dt = datetime.fromisoformat(val)
    return str(dt - timedelta(microseconds = dt.microsecond))

#===============================================
def reportDS(output, ds_info, mongo_agent, base_ds_info = None):
    date_loaded = ds_info.get("date_loaded")
    if date_loaded is None:
        date_loaded = datetime.now().isoformat()
    date_created = mongo_agent.getCreationDate()
    if date_created == date_loaded:
        date_loaded = None

    startHtmlReport(output, "Anfisa dataset %s report" % ds_info["name"],
        "receipt" in ds_info and ds_info["receipt"].get("kind") == "tree")
    print('  <body>', file = output);
    print('    <table class="report-main">', file = output)

    for key, title, val in [
            ("name", "Name", None),
            ("kind", "Kind", None),
            ("total", "Variants", None),
            (None, "Created at", reprDateVal(date_created)),
            (None, "Reloaded at", reprDateVal(date_loaded)),
            (None, "Base dataset", base_ds_info["name"]
                if base_ds_info is not None else None),
            (None, "Base variants", base_ds_info["total"]
                if base_ds_info is not None else None),
            (None, "Base loaded at", reprDateVal(base_ds_info["date_loaded"])
                if base_ds_info is not None else None)]:
        if key is not None:
            val = ds_info.get(key)
        if val is None:
            continue
        val = str(val)
        print('<tr><td class="rep-title">%s</td>' % escape(title),
            file = output)
        print('<td class="rep-val">%s<td></tr>' % escape(val), file = output)
    print('    </table>', file = output)

    if ("versions" in ds_info["meta"]
            and len(ds_info["meta"]["versions"]) > 0):
        versions = ds_info["meta"]["versions"]
        print('<h2>Annotation sources versions</h2>', file = output)
        print('<table class="report-anno">', file = output)
        for name in sorted(versions.keys()):
            print('<tr><td class="anno-src">%s</td>' % escape(name),
                file = output)
            print('<td class="anno-ver">%s</td></tr>' %
                escape(str(versions[name])), file = output)
        print('</table>', file = output)

    if "receipt" in ds_info:
        receipt = ds_info["receipt"]
        if receipt["kind"] == "filter":
            print('<h2>Applied filter</h2>', file = output)
            print('<table class="report-filter">', file = output)
            for instr in receipt["seq"]:
                print('<tr><td>%s</td></tr>' % escape(instr), file = output)
            print('</table>', file = output)
        else:
            assert receipt["kind"] == "tree"
            print('<h2>Applied tree code</h2>', file = output)
            for key_t, title_t in [
                    ("std", "Based on"),
                    ("version", "Version")]:
                if key not in receipt:
                    continue
                print('<p class="tree-info">%s: %s</p>' %
                    (escape(title_t), escape(receipt[key])), file = output)
            print('<table class="report-tree">', file = output)
            for instr, count, ret_mode in receipt["points"]:
                print('<tr><td class="tree-point"><div class="highlight">' +
                    instr + '</div></td>', file = output)
                if count is None:
                    print('<td></td>', file = output)
                elif ret_mode:
                    print('<td class="point-ok">+%d</td>' % count,
                        file = output)
                elif ret_mode is False:
                    print('<td class="point-drop">-%d</td>' % count,
                        file = output)
                else:
                    print('<td class="point-ign">%d</td>' % count,
                        file = output)
            print('</table>', file = output)

    print('  </body>', file = output);
    print('</html>', file = output);
