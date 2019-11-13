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

from .gen_html import startHtmlPage
from .html_xl import formNoteDiv, formCreateWsDiv, formSubViewDiv
#===============================================
def formXLTreePage(output, common_title, html_base, xl_ds, ws_url):
    startHtmlPage(output,
        common_title + "-XL " + xl_ds.getName() + "(d-tree)", html_base,
        css_files = ["xltree.css", "py_pygments.css", "base.css"],
        js_files = ["xltree.js", "fctrl.js",
            "xl_ctrl.js", "base.js"])

    print('  <body onload="setupXLTree(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_url), file = output)

    _formXLPannel(output, xl_ds)
    _formCurCondDiv(output)
    _formVersionsDiv(output)
    _formEditCodeDiv(output)
    formNoteDiv(output)
    formCreateWsDiv(output)
    formSubViewDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formXLPannel(output, ds):
    print('''
      <div id="xl-ctrl">
        <div id="xl-info">
            <span id="control-wrap" title="Control Menu..." class="drop">
                <span id="control-open" class="drop"
                    onclick="openControlMenu();">&#8285;</span>
                <div id="control-menu" class="drop">
                    <div onclick="goHome();"
                        class="drop ctrl-menu">Home Directory</div>
                    <div onclick="goToPage(\'DOC\');" id="menu-doc"
                        class="drop ctrl-menu">Documentation</div>
                    <div onclick="goToPage(\'XL\');"
                        class="drop ctrl-menu">Filtering pannel</div>
                    <div onclick="openNote();"
                        class="drop ctrl-menu">Dataset Note...</div>
                    <div onclick="wsCreate();"
                        class="drop ctrl-menu">Create workspace...</div>
                </div>
            </span>&emsp;
            XL dataset: <span id="xl-name"></span><br/>
            <select id="std-code-select" onchange="pickStdCode();"
                title="Pick tree code from repository">
                <option value="">in work</option>''', file = output)
    for std_name in ds.getCondEnv().getStdTreeCodeNames():
        print('                <option value="%s">%s</option>' % (
            escape(std_name), escape(std_name)), file = output)
    print('''
            </select>
            <button id="code-edit-show" onclick='sCodeEditH.show();'>
                Edit code
            </button>
        </div>
        <div id="xl-tree-info">
            Accepted: <span id="report-accepted"></span>&emsp;
            Rejected: <span id="report-rejected"></span><br/>
            <div id="tree-ctrl">
              <button id="tree-undo" title="Undo" class="action"
                onclick='treeUndo();'> &#8630;
              </button>
              <button id="tree-redo" title="Redo" class="action"
                onclick='treeRedo();'> &#8631;
              </button>
              <span id="tree-current-version" title="tree version"
                 onclick="modVersions();"></span>
              <button id="tree-version" class="action" title="Save version"
                onclick='treeVersionSave();'> Save
              </button>
            </div>
        </div>
        <div id="xl-cur-info">
            Variants in scope: <span id="list-report"></span><br/>
            <button id="xl-sub-view"
                onclick="sSubViewH.show()">View variants</button>
        </div>
      </div>
      <div id="xl-main">
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
def _formVersionsDiv(output):
    print('''
    <div id="versions-back" class="modal-back">
      <div id="versions-mod">
        <div id="versions-title">
            Versions
              <span class="close-it" onclick="modalOff();">&times;</span>
        </div>
        <div id="versions-main">
            <div id="versions-list-wrap">
                <div id="versions-tab"></div>
            </div>
            <div id="versions-cmp-wrap">
                <div id="versions-cmp"></div>
            </div>
        </div>
        <div id="versions-ctrl">
            <button class="action" onclick="modalOff();">
                Done
            </button>
            <button id="btn-version-select" class="action" title="Select version"
                onclick='versionSelect();'> Select
            </button>
            <span id="versions-ctrl-sep"></span>
            <button id="btn-version-delete" class="action" title="Delete version"
                onclick='versionDelete();'> Delete
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
            <span id="code-edit-title">Edit decision tree code</span>
              <span class="close-it" onclick="sViewH.modalOff();">&times;</span>
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

