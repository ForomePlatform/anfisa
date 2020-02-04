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
def reportRecord(output, ds_h, rec_no, details = None, port = -1):
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

    print('<body onload="init_r(%d, \'%s\', %d, %s, \'%s\');">' % (port,
        ds_h.getLastAspectID() if port == 1 else ds_h.getFirstAspectID(),
        rec_no, use_tags, ds_h.getName()), file = output)

    print('<div id="r-tab">', file = output)
    print('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>',
        file = output)

    asp_data_seq = ds_h.getViewRepr(rec_no, details)
    for asp_data in asp_data_seq:
        print('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (asp_data["kind"], asp_data["name"], asp_data["name"],
            AnfisaConfig.decorText(asp_data["title"])), file = output)
    if use_tags == "true":
        tags_asp_name = AnfisaConfig.configOption("aspect.tags.name")
        print('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            ("tech",  tags_asp_name, tags_asp_name,
            AnfisaConfig.textMessage("aspect.tags.title")), file = output)
    print('</div>', file = output)

    print('<div id="r-cnt-container">', file = output)
    for asp_data in asp_data_seq:
        print('<div id="a--%s" class="r-tabcnt">' %
            asp_data["name"], file = output)
        _reportAspect(output, asp_data)
        print('</div>', file = output)
    if use_tags == "true":
        print(('<div id="a--%s" class="r-tabcnt">' % tags_asp_name),
            file = output)
        tagsBlock(output)
        print('</div>', file = output)

    print('</div>', file = output)
    print('</body>', file = output)
    print('</html>', file = output)

#===============================================
def _reportAspect(output, rep_data):
    if rep_data["type"] == "table":
        n_col = rep_data["columns"]
        print('<table id="rec-%s">' % rep_data["name"], file = output)
        if rep_data.get("colhead"):
            print('<tr class="head"><td class="title"></td>', file = output)
            for title, count in rep_data["colhead"]:
                print('<td class="title" colspan="%d">%s</td>' %
                (count, title), file = output)
            print('</tr>', file = output)

        for attr_data in rep_data["rows"]:
            if len(attr_data) == 0:
                print('<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                    (n_col + 1), file = output)
                continue
            print('<tr>', file = output)
            if len(attr_data) > 3:
                print('<td class="title" title="%s">%s</td>' % (
                    escape(attr_data[3]), attr_data[1]), file = output)
            else:
                print('<td class="title">%s</td>' % attr_data[1],
                    file = output)
            for val, class_name in attr_data[2]:
                print('<td class="%s">%s</td>' % (class_name, val),
                    file = output)
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
