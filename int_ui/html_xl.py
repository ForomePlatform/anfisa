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

import int_ui.gen_html as gen_html
#===============================================
def formXLPage(output, common_title, html_base, xl_ds, ws_pub_url):
    gen_html.startHtmlPage(output, common_title + "-XL " + xl_ds.getName(),
        html_base,
        css_files = ["xl.css", "filters.css", "eval.css",
            "vrec.css", "base.css"],
        js_files = ["xl.js", "filters.js", "eval.js", "func.js",
            "vrec.js", "base.js"])

    print('  <body onload="setupXLFilters(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_pub_url), file = output)
    _formPanel(output)
    gen_html.formFilterPanel(output)
    gen_html.formNoteDiv(output)
    gen_html.formCreateWsDiv(output)
    gen_html.formSubViewDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formPanel(output):
    print('''
      <div id="xl-top">
        <div id="xl-top-ctrl-left">
          <div class="dropdown">
            <span id="control-open">&#8285;</span>
            <div id="control-menu" class="dropdown-content">
              <a class="popup" onclick="goHome();">Home Directory</a>
              <a class="popup" onclick="goToPage(\'DOC\');"
                id="menu-doc">Documentation</a>
              <a class="popup" onclick="goToPage(\'DTREE\');"
                >Decision tree panel</a>
              <a class="popup" onclick="openNote();"
                >Dataset Note...</a>
              <a class="popup" onclick="showExport();"
                >Export...</a>
              <a class="popup" onclick="wsCreate();"
                >Derive dataset...</a>
            </div>
          </div>
          <div id="export-result" class="popup"></div>
          &emsp;
          XL dataset: <span id="ds-name" class="bold"></span><br/>
          Variants: <span id="list-report" class="bold"></span>
        </div>
        <div id="xl-top-ctrl-right">
            <button id="open-sub-view-rec"
                onclick="sSubVRecH.show()">View variants</button>
        </div>
      </div>''', file = output)
#===============================================
