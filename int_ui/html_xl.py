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

from .gen_html import startHtmlPage, formFilterPanel, formNoteDiv

#===============================================
def formXLPage(output, common_title, html_base, xl_ds, ws_pub_url):
    startHtmlPage(output, common_title + "-XL " + xl_ds.getName(), html_base,
        css_files = ["base.css", "vrec.css", "filters.css", "xl.css"],
        js_files = ["xl.js", "filters.js", "sub_vrec.js",
            "fctrl.js", "xl_ctrl.js", "base.js"])

    print('  <body onload="setupXLFilters(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_pub_url), file = output)

    _formXLPanel(output, xl_ds.getName())
    formNoteDiv(output)
    formCreateWsDiv(output)
    formSubViewDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formXLPanel(output, ds_name):
    print('''
      <div id="xl-top">
        <div id="xl-top-ctrl-left">
          <div class="dropdown">
            <span id="control-open">&#8285;</span>
            <div id="control-menu" class="dropdown-content">
              <a class="drop" onclick="goHome();">Home Directory</a>
              <a class="drop" onclick="goToPage(\'DOC\');"
                id="menu-doc">Documentation</a>
              <a class="drop" onclick="goToPage(\'DTREE\');"
                >Decision tree panel</a>
              <a class="drop" onclick="openNote();"
                >Dataset Note...</a>
              <a class=:drop" onclick="showExport();"
                >Export...</a>
              <a class=:drop" onclick="wsCreate();"
                >Create workspace...</a>
            </div>
          </div>
          <div id="export-result" class="drop"></div>
          &emsp;
          XL dataset: <span id="ds-name" class="bold"></span><br/>
          Variants: <span id="list-report" class="bold"></span>
        </div>
        <div id="xl-top-ctrl-right">
            <button id="open-sub-view-rec"
                onclick="sSubVRecH.show()">View variants</button>
        </div>
      </div>''', file = output)
    formFilterPanel(output)

#===============================================
def formCreateWsDiv(output):
    print('''
    <div id="create-ws-back" class="modal-back">
      <div id="create-ws-mod">
        <div id="create-ws-top">
            <span id="create-ws-title"></span>
              <span class="close-it"
                onclick="sViewH.modalOff();">&times;</span>
        </div>
        <div id="create-ws-main">
            <div>Workspace name:
                <input id="create-ws-name" type="text">
            </div>
            <div id="create-ws-problems"></div>
            <div id="create-ws-status"></div>
        </div>
        <div id="create-ws-ctrl">
            <button id="create-ws-start" onclick="startWsCreate();">
              Start...
            </button>
            <button id="create-ws-cancel" onclick="sViewH.modalOff();">
              Cancel
            </button>
        </div>
      </div>
    </div>
''', file = output)

#===============================================
def formSubViewDiv(output):
    print('''
    <div id="sub-view-back" class="modal-back">
      <div id="sub-view-status"></div>
      <div id="sub-view-mod">
        <div id="sub-view-left">
            <div id="sub-view-ctrl">
                <span id="sub-view-list-report"></span><br/>
                <input id="sub-view-check-full" type="checkbox"
                    onchange="sSubVRecH.setMode(0);"/>
                <label for="sub-view-check-full">
                <span id="sub-view-mod-full">Full list</span></label><br/>
                <input id="sub-view-check-samples" type="checkbox"
                    onchange="sSubVRecH.setMode(1);"/>
                <label for="sub-view-check-samples">
                <span id="sub-view-mod-samples">Samples-25</span></label><br/>
            </div>
            <div id="sub-view-wrap-list">
                <div id="sub-view-list">
                </div>
            </div>
        </div>
        <div id="sub-view-right">
            <div id="sub-view-rec-info">
                <span id="sub-view-title"></span>
                <span class="close-it"
                    onclick="sViewH.modalOff();">&times;</span>
            </div>
            <div id="sub-view-rec-wrap">
                <iframe id="sub-view-rec-frame"
                    name="rec-frame1" src="norecords">
                </iframe>
        </div>
      </div>
    </div>
''', file = output)
