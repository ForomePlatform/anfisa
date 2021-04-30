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

from xml.sax.saxutils import escape
from app.config.a_config import AnfisaConfig
from .gen_html import tagsBlock, startHtmlPage
#===============================================
def fullRecordView(output, ds_h, rec_no,
        details = None, active_samples = None, port = -1):
    css_files = ["rec.css", "base.css"]
    js_files = ["rec.js", "base.js"]
    use_tags = "false"
    if ds_h.getDSKind() == "ws" and port >= 0:
        css_files.append("tags.css")
        js_files.append("tags.js")
        use_tags = "true"
    else:
        assert port < 1
    startHtmlPage(output, css_files = css_files, js_files = js_files)

    aspect_id = (ds_h.getLastAspectID()
        if port == 1 else ds_h.getFirstAspectID())

    print(f'<body onload="init_r({port}, \'{aspect_id}\', {rec_no}, '
        f'{use_tags}, \'{ds_h.getName()}\');">', file = output)

    print('<div id="r-tab">', file = output)
    print('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>',
        file = output)

    asp_data_seq = ds_h.getViewRepr(rec_no, details, active_samples)
    for asp_data in asp_data_seq:
        asp_ref_title = AnfisaConfig.decorText(asp_data["title"])
        print(f'<button class="r-tablnk {asp_data["kind"]}" '
            f'id="la--{asp_data["name"]}" '
            f'onclick="pickAspect(\'{asp_data["name"]}\')">'
            f'{asp_ref_title}</button>', file = output)
    if use_tags == "true":
        tags_asp_name = AnfisaConfig.configOption("aspect.tags.name")
        asp_title = AnfisaConfig.textMessage("aspect.tags.title")
        print(f'<button class="r-tablnk tech" id="la--{tags_asp_name}" '
            f'onclick="pickAspect(\'{tags_asp_name}\')">{asp_title}</button>',
            file = output)
    print('</div>', file = output)

    print('<div id="r-cnt-container">', file = output)
    for asp_data in asp_data_seq:
        print(f'<div id="a--{asp_data["name"]}" class="r-tabcnt">',
            file = output)
        _reportAspect(output, asp_data)
        print('</div>', file = output)
    if use_tags == "true":
        print(f'<div id="a--{tags_asp_name}" class="r-tabcnt">',
            file = output)
        tagsBlock(output)
        print('</div>', file = output)

    print('</div>', file = output)
    print('</body>', file = output)
    print('</html>', file = output)

#===============================================
def _reportAspect(output, rep_data):
    if rep_data["type"] == "table":
        if rep_data.get("parcontrol"):
            print(rep_data["parcontrol"], file = output)
        n_col = rep_data["columns"]
        print(f'<table id="rec-{rep_data["name"]}">', file = output)
        if rep_data.get("colgroup"):
            print('<colgroup>', file = output)
            for col_class in rep_data["colgroup"]:
                print(f'  <col class="{col_class}"/>', file = output)
            print('</colgroup>', file = output)
        if rep_data.get("colhead"):
            print('<tr class="head"><td class="title"></td>', file = output)
            for title, count, add_class in rep_data["colhead"]:
                print(f'<td class="title {add_class}" '
                    f'colspan="{count}">{title}</td>', file = output)
            print('</tr>', file = output)
        for row_data in rep_data["rows"]:
            if row_data is None:
                print(f'<tr><td colspan="{n_col + 1}" '
                    'class="title">&emsp;</td></tr>', file = output)
                continue
            print('<tr>', file = output)
            op_tooltip = (f' title="{escape(row_data["tooltip"])}"'
                if "tooltip " in row_data else '')
            print(f'<td class="title"{op_tooltip}>'
                f'{escape(row_data["title"])}</td>', file = output)
            for val, class_name in row_data["cells"]:
                print(f'<td class="{class_name}">{val}</td>', file = output)
            print('</tr>', file = output)
        print('</table>', file = output)
    else:
        assert rep_data["type"] == "pre"
        if "content" in rep_data:
            print('<pre>', file = output)
            print(rep_data["content"], file = output)
            print('</pre>', file = output)
        else:
            print('<p class="error">No input data</p>', file = output)
