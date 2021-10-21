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

from .gen_html import startHtmlPage
#===============================================
def formDocNavigationPage(output, common_title, html_base, ds_h):
    doc_seq = ds_h.getDataInfo().get("doc")
    assert doc_seq is not None
    startHtmlPage(output,
        common_title + "-DOC %s" % ds_h.getName(), html_base,
        css_files = ["doc_nav.css", "base.css"],
        js_files = ["doc_nav.js", "base.js"])

    print(f'  <body onload="initReportPage(\'{ds_h.getName()}\', '
        f'\'{ds_h.getDSKind()}\', \'{common_title}\');">', file = output)
    print('''
    <div id="all">
      <div id="left">
        <div id="doc-list">
        </div>
      </div>
      <div id="right">
        <div id="title">
            <span id="ds-name" onclick="goToPage(\'\');"></span>:
            <span id="doc-title"></span>
        </div>
        <iframe id="doc-content" name="doc-content">
        </iframe>
      </div>
    </div>''', file = output)
    print('  </body>', file = output)
