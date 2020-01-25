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

    use_pygments = False
    if "receipts" in ds_info:
        for receipt in ds_info["receipts"]:
            if receipt.get("kind") == "dtree":
                use_pygments = True
                break

    info_sheet = [ (title, ds_info[key]) for title, key in
        [("Name", "name"), ("Kind", "kind"), ("Variants", "total")]
    ]
    info_sheet.append(("Created at", reprDateVal(date_created)))
    info_sheet.append(("Reloaded at", reprDateVal(date_loaded)))
    if ds_info["base"] != ds_info["name"]:
        info_sheet.append(("Base dataset", ds_info["base"]))
    if base_ds_info:
        info_sheet.append(("Base variants", base_ds_info["total"]))
        info_sheet.append(("Base loaded at",
            reprDateVal(base_ds_info["date_loaded"])))
    if ds_info["root"] != ds_info["base"]:
        info_sheet.append(("Root dataset", ds_info["root"]))

    startHtmlReport(output, "Anfisa dataset %s report" % ds_info["name"],
        use_pygments)
    print('  <body>', file = output)
    print('    <table class="report-main">', file = output)
    for title, val in info_sheet:
        if val is None:
            continue
        print('    <tr><td class="rep-title">%s</td>' % escape(title),
            file = output)
        print('    <td class="rep-val">%s<td></tr>' % escape(str(val)),
            file = output)
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

    if "receipts" in ds_info:
        for idx, receipt in enumerate(ds_info["receipts"]):
            _reportReceipt(output, idx, receipt)

    print('  </body>', file = output)
    print('</html>', file = output)

#===============================================
def _reportReceipt(output, idx_receipt, receipt):
    if receipt["kind"] == "filter":
        print('<h2>Filter applied in %s</h2>'
            % escape(receipt["base"]), file = output)
        if "filter-name" in receipt:
            print("<p>Filter name:", '<b>' + escape(receipt["filter-name"])
                + '</b>', file = output)
            if "eval-update-info" in receipt:
                updated_time, updated_from = receipt["eval-update-info"]
                print("updated at", reprDateVal(updated_time),
                    "from", updated_from, file = output)
            print("</p>", file = output)
        print('<table class="report-filter">', file = output)
        for instr in receipt["seq"]:
            print('<tr><td>%s</td></tr>' % escape(instr), file = output)
        print('</table>', file = output)
    else:
        assert receipt["kind"] == "dtree"
        print('<h2>Decision tree code applied in %s</h2>'
            % escape(receipt["base"]), file = output)
        if "dtree-name" in receipt:
            print("<p>Tree name:", '<b>' + escape(receipt["dtree-name"])
                + '</b>', file = output)
            if "eval-update-info" in receipt:
                updated_time, updated_from = receipt["eval-update-info"]
                print("updated at", reprDateVal(updated_time),
                    "from", updated_from, file = output)
            print("</p>", file = output)
        print('<table class="report-dtree">', file = output)
        for instr, count, ret_mode in receipt["points"]:
            print('<tr><td class="dtree-point"><div class="highlight">'
                + instr + '</div></td>', file = output)
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
