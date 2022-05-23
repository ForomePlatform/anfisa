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
def formDTreePage(output, common_title, html_base, ds_h, ws_pub_url):
    gen_html.startHtmlPage(output,
        common_title + "-DTree " + ds_h.getName(), html_base,
        css_files = ["dtree.css", "eval.css", "py_pygments.css",
            "vrec.css", "base.css"],
        js_files = ["dtree.js", "eval.js", "func.js", "vrec.js", "base.js"])

    print(f'  <body onload="setupDTree(\'{ds_h.getName()}\', '
        f'\'{ds_h.getDSKind()}\',  \'{common_title}\', \'{ws_pub_url}\');">',
        file = output)

    _formPanel(output)
    _formCurCondDiv(output)
    _formCmpCodeDiv(output)
    _formEditCodeDiv(output)

    gen_html.formNoteDiv(output)
    gen_html.formDeriveWsDiv(output)
    gen_html.formSubViewDiv(output)
    gen_html.formUnitClassesDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formPanel(output):
    print('''
      <div id="dtree-ctrl">
        <div id="dtree-top-ctrl">
          <div class="dropdown">
            <span id="control-open">&#8285;</span>
            <div id="control-menu" class="dropdown-content">
                <a class="popup" onclick="goHome();">Home Directory</a>
                <a class="popup" onclick="goToPage(\'DOC\');"
                    id="menu-doc">Documentation</a>
                <a class="popup" onclick="goToPage(\'\');"
                    >Dataset main page</a>
                <a class="popup" onclick="openNote();"
                    >Dataset Note...</a>
                <a class="popup" onclick="wsCreate();"
                    >Derive dataset...</a>
            </div>
          </div>&emsp;
          Dataset: <span id="ds-name" class="bold"></span><br/>
            <div id="dtree-edit-ctrl">
              <div class="dropdown">
                <button class="op-button popup">Decision Trees...</button>
                <div id="dtree-op-list" class="dropdown-content">
                  <a class="popup" id="dtree-op-load"
                    onclick="sDTreesH.startLoad();">Load</a>
                  <a class="popup" id="dtree-op-create"
                    onclick="sDTreesH.startCreate();">Create</a>
                  <a class="popup"  id="dtree-op-modify"
                    onclick="sDTreesH.startModify();">Modify</a>
                  <a class="popup"  id="dtree-op-delete"
                    onclick="sDTreesH.deleteIt();">Delete</a>
                </div>
              </div>
              <div id="dtree-name-combo" class="combobox">
                <select id="dtree-name-combo-list"
                        onchange="sDTreesH.select();">
                    <option value=""></option>
                </select>
                <input id="dtree-name-input" type="text">
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
        <div id="dtree-unit-classes">
            <span id="unit-classes-state"></span>
            <button onclick="sEvalCtrlH.show();"
                title="Select filtration properties in work">&#9745;</button>
        </div>
      </div>
      <div id="dtree-main" class="panel-space">
        <div id="panel-tree">
          <div id="decision-tree" class="list-items">
          </div>
        </div>
        <div id="panel-stat">
          <div id="function-list">
            <span class="note">Functions:</span>
            <select id="function-name-select"
                onchange="sEvalCtrlH.checkFunctionSelect();">
                <option value=""></option>
            </select>
          </div>
          <div id="stat-list" class="list-items">
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
                <span class="close-it"
                    onclick="sViewH.modalOff();">&times;</span>
            </div>
            <div id="cond-message"></div>''', file = output)

    gen_html.formCurConditionControls(output)

    print('''
            <div id="cond-ctrl">
                <button id="cond-button-atom-set"
                    title="Tune settings of the condition"
                    onclick="modifyDTree('ATOM', 'EDIT');"> Set
                </button>
                <button id="cond-button-point-insert" title=
                    "Insert the condition before current instruction"
                    onclick="modifyDTree('POINT', 'INSERT');"> Insert
                </button>
                <button id="cond-button-point-join-and" title=
                    "Join the condition with instruction by and-operation"
                    onclick="modifyDTree('POINT', 'JOIN-AND');"> Join by AND
                </button>
                <button id="cond-button-point-join-or"
                    title="Join the condition with instruction by or-operation"
                    onclick="modifyDTree('POINT', 'JOIN-OR');"> Join by OR
                </button>
                <button id="cond-button-point-up-join-and" title=
                    "Join the condition to upper instruction by and-operation"
                    onclick="modifyDTree('POINT', 'UP-JOIN-AND');"> Join by AND
                </button>
                <button id="cond-button-point-up-join-or" title=
                    "Join the condition to upper instruction by or-operation"
                    onclick="modifyDTree('POINT', 'UP-JOIN-OR');"> Join by OR
                </button>
                &emsp;&emsp;
                <button id="cond-button-point-replace"
                    title="Replace whole instruction by this condition"
                    onclick="modifyDTree('POINT', 'REPLACE');"> Replace
                </button>
                <button id="cond-button-point-up-replace"
                    title="Replace whole upper instruction by this condition"
                    onclick="modifyDTree('POINT', 'UP-REPLACE');"> Replace
                </button>
                <button id="cond-button-atom-delete"
                    title="Remove the condition from instruction"
                    onclick="modifyDTree('ATOM', 'DELETE');">Delete
                </button>
                <button id="cond-button-point-delete"
                    title="Delete the instruction"
                    onclick="modifyDTree('POINT', 'DELETE');">
                        Delete instruction
                </button>
                &emsp;&emsp;
                <button onclick="sViewH.modalOff();">
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
              <span class="close-it"
                onclick="sViewH.modalOff();">&times;</span>
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
            <button class="action" onclick="sViewH.modalOff();">
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
