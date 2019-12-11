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

from .gen_html import startHtmlPage, formNoteDiv
from .html_xl import formCreateWsDiv, formSubViewDiv
#===============================================
def formDTreePage(output, common_title, html_base, ds_h, ws_pub_url):
    js_files = ["dtree.js", "fctrl.js", "sub_vrec.js", "xl_ctrl.js", "base.js"]
    startHtmlPage(output,
        common_title + "-DTree " + ds_h.getName(), html_base,
        css_files = ["dtree.css", "py_pygments.css", "vrec.css", "base.css"],
        js_files = js_files)

    print('  <body onload="setupDTree(\'%s\', \'%s\',  \'%s\', \'%s\');">' %
        (ds_h.getName(), ds_h.getDSKind(), common_title, ws_pub_url),
        file = output)

    _formDTreePanel(output, ds_h)
    _formCurCondDiv(output)
    _formCmpCodeDiv(output)
    _formEditCodeDiv(output)
    formNoteDiv(output)

    formCreateWsDiv(output)
    formSubViewDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formDTreePanel(output, ds_h):
    print('''
      <div id="dtree-ctrl">
        <div id="dtree-top-ctrl">
          <div class="dropdown">
            <span id="control-open">&#8285;</span>
            <div id="control-menu" class="dropdown-content">
                <a class="drop" onclick="goHome();">Home Directory</a>
                <a class="drop" onclick="goToPage(\'DOC\');"
                    id="menu-doc">Documentation</a>
                <a class="drop" onclick="goToPage(\'\');"
                    >Dataset main page</a>
                <a class="drop" onclick="openNote();"
                    >Dataset Note...</a>
                <a class=:drop" onclick="wsCreate();"
                    >Create workspace...</a>''',
            file = output)
    print('''
            </div>
          </div>&emsp;
          Dataset: <span id="ds-name" class="bold"></span><br/>
            <div id="dtree-edit-ctrl">
              <div class="dropdown">
                <button class="op-button drop">Decision Trees...</button>
                <div id="dtree-op-list" class="dropdown-content">
                  <a class="drop" id="dtree-op-load"
                    onclick="sDTreesH.startLoad();">Load</a>
                  <a class="drop" id="dtree-op-create"
                    onclick="sDTreesH.startCreate();">Create</a>
                  <a class="drop"  id="dtree-op-modify"
                    onclick="sDTreesH.startModify();">Modify</a>
                  <a class="drop"  id="dtree-op-delete"
                    onclick="sDTreesH.deleteIt();">Delete</a>
                </div>
              </div>
              <div id="dtree-name-combo" class="combobox">
                <select id="dtree-name-combo-list"
                        onchange="sDTreesH.select();">
                    <option value=""></option>
                    <input id="dtree-name-input" type="text" />
                </select>
              </div>
              <button id="dtree-act-op" class="op-button"
                onclick="sDTreesH.action();">...</button>
            </div>
        </div>
        <div id="dtree-top-info">
            Accepted: <span id="report-accepted"></span>&emsp;
            Rejected: <span id="report-rejected"></span><br/>
            <div id="tree-ctrl">
              <button id="code-edit-show" onclick='sCodeEditH.show();'>
                Edit code
              </button>
              <button id="dtree-undo" title="Undo" class="action"
                onclick='sHistoryH.doUndo();'> &#8630;
              </button>
              <button id="dtree-redo" title="Redo" class="action"
                onclick='sHistoryH.doRedo();'> &#8631;
              </button>
              <button onclick='sDecisionTree.clear();'>
                Clear
              </button>
            </div>
        </div>
        <div id="dtree-top-cur">
            Variants in scope:
                <span id="list-report" class="bold"></span><br/>
            <button id="open-sub-view-rec"
                onclick="sSubVRecH.show()">View variants</button>
        </div>
      </div>
      <div id="dtree-main">
        <div id="panel-tree">
          <div id="decision-tree">
          </div>
        </div>
        <div id="panel-stat">
          <div id="stat-list">
          </div>
        </div>
      </div>''', file = output)

#===============================================
def _formCurCondDiv(output):
    print('''
    <div id="cur-cond-back">
      <div id="cur-cond-mod">
        <div id="condition-change">
            <div id="cond-title-wrap">
                <span id="cond-title"></span>
                <span class="close-it" onclick="modalOff();">&times;</span>
            </div>
            <div id="cond-message"></div>
            <div id="cur-cond-numeric">
              <span id="cond-min" class="num-set"></span>
              <input id="cond-min-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-sign"></span>
              <input id="cond-max-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-max" class="num-set"></span>
              <span id="num-count" class="num-count"></span>
            </div>
            <div id="cur-cond-enum">
              <div id="cur-cond-zyg-problem-group"></div>
              <div id="wrap-cond-enum">
                <div id="cur-cond-enum-list">
                    <div id="op-enum-list">
                    </div>
                </div>
                <div id="cur-cond-enum-ctrl">
                  <div id="cur-cond-enum-zeros">
                    <label for="cur-enum-zeros">Show zeros&nbsp;</label><input
                        id="cur-enum-zeros" type="checkbox"
                        onchange="sOpEnumH.careEnumZeros();"/>
                  </div>
                  <div id="cur-cond-enum-mode">
                    <span id="cond-mode-and-span">
                      <input id="cond-mode-and" type="checkbox"
                        onchange="sOpEnumH.checkControls(1);"
                        /><label for="cond-mode-and">&nbsp;all</label>
                    </span><br/>
                    <span id="cond-mode-not-span">
                      <input id="cond-mode-not" type="checkbox"
                        onchange="sOpEnumH.checkControls(2);"
                        /><label for="cond-mode-not">&nbsp;not</label>
                    </span><br/>
                  </div>
                </div>
              </div>
            </div>
            <div id="cur-cond-loading">
                <div class="loading">Loading data...</div>
            </div>
            <div id="cond-ctrl">
                <button id="cond-button-set" onclick="fixMark();">
                    Set
                </button>
                <button onclick="modalOff();">
                    Cancel
                </button>
            </div>
        </div>
      </div>
    </div>''', file = output)

#===============================================
def _formCmpCodeDiv(output):
    print('''
    <div id="cmp-code-back" class="modal-back">
      <div id="cmp-code-mod">
        <div id="cmp-code-title">
            Compare decision trees
              <span class="close-it" onclick="modalOff();">&times;</span>
        </div>
        <div id="cmp-code-main">
            <div id="cmp-code-list-wrap">
                <div id="cmp-code-tab"></div>
            </div>
            <div id="cmp-code-cmp-wrap">
                <div id="cmp-code-cmp"></div>
            </div>
        </div>
        <div id="cmp-code-ctrl">
            <button class="action" onclick="modalOff();">
                Done
            </button>
            <button id="btn-version-select" class="action"
                title="Select version" onclick='versionSelect();'> Select
            </button>
            <span id="cmp-code-ctrl-sep"></span>
            <button id="btn-version-delete" class="action"
                title="Delete version" onclick='versionDelete();'> Delete
            </button>
        </div>
      </div>
    </div>
''', file = output)

#===============================================
def _formEditCodeDiv(output):
    print('''
    <div id="code-edit-back" class="modal-back">
      <div id="code-edit-mod">
        <div id="code-edit-top">
            <span id="code-edit-title">Edit current decision tree code</span>
              <span class="close-it"
                onclick="sViewH.modalOff();">&times;</span>
        </div>
        <div id="code-edit-ctrl">
            <button id="code-edit-drop" onclick="sCodeEditH.drop();">
                Drop changes
            </button>
            <button onclick="sViewH.modalOff();">
                Done
            </button>
            <button id="code-edit-save" onclick="sCodeEditH.save();">
                Save
            </button>
            <span id="code-edit-error"
                onclick="sCodeEditH.posError();"></span>
        </div>
        <div id="code-edit-main">
            <textarea id="code-edit-content"
                oninput="sCodeEditH.checkContent();"></textarea>
        </div>
      </div>
    </div>
''', file = output)
