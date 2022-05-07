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
def formGenesPage(output, common_title, html_base, ds_h):
    startHtmlPage(output,
        common_title + "-Genes %s" % ds_h.getName(), html_base,
        css_files = ["genes.css", "base.css"],
        js_files = ["genes.js", "base.js"])

    print(f'  <body onload="initGenesPage(\'{ds_h.getName()}\', '
        f'\'{ds_h.getDSKind()}\', \'{common_title}\');">', file = output)
    print('''
    <div id="all">
      <div id="top">
        <div id="gene-ctrl">
          <div id="sel-panel">
            <input id="sel-check-panel" type="checkbox"
                onchange="checkSel(0);"/>
           Panels: <span id="gene-versions">&#x1F6C8;</span><br/>
            <select id="panel-select" onclick="checkSel(0)" onchange="pickPanel();">
                <option value=""></option>
            </select>
          </div>
          <div id="sel-pattern">
            <input id="sel-check-pattern" type="checkbox"
                onchange="checkSel(1);"/>
            Pattern: <br/>
            <input id="pattern-input" type="text" onchange="pickPattern();"/>
            <button id="pattern-find"
                class="op-button" onclick="pickPattern();">
              Find
            </button>
          </div>
        </div>
        <div id="dyn-panel-ctrl">
          <div id="sel-active-dyn">
            <input id="sel-check-dyn-active" type="checkbox"
                onchange="checkDynSel(0);"/>Active gene list
          </div>
          <div id="sel-dyn-panel">
            <input id="sel-check-dyn-panel" type="checkbox"
                onchange="checkDynSel(1);"/>
            <div class="dropdown">
              <button class="op-button popup">
                Panels...
              </button>
              <div id="dyn-panels-op-list" class="dropdown-content">
                <a class="popup"  id="dyn-panels-op-new"
                    onclick="startDynPanelNew();">New panel</a>
                <a class="popup" id="dyn-panels-op-save-as"
                    onclick="startDynPanelSaveAs();">Save as</a>
                <a class="popup"  id="dyn-panels-op-join"
                    onclick="dynPanelJoin();">Join to active</a>
                <a class="popup"  id="dyn-panels-op-delete"
                    onclick="startDynPanelDelete();">Delete</a>
              </div>
            </div>
            <div id="dyn-panels-name-combo" class="combobox">
              <select id="dyn-panels-combo-list"
                  onchange="checkDynSel(1);">
              </select>
              <input id="dyn-panels-name-input" type="text" />
            </div>
          </div>
          <div id="sel-dyn-options">
              <button class="op-button" id="dyn-panels-op-save"
                onclick='dynPanelSave();'>
                Save
              </button>
              <button class="op-button" id="dyn-panels-op-drop"
                onclick='dynPanelDrop();'>
                Drop changes
              </button>
              &emsp;
              <button id="dyn-panels-op-act" class="op-button"
                onclick="dynPanelAct();">
                ...
              </button>
          </div>
        </div>
      </div>
      <div id="bottom">
        <div id="left">
          <div id="symbol-list-wrap">
            <div id="symbol-list" class="symbol-list">
            </div>
          </div>
        </div>
        <div id="center">
          <div id="symbol-ctrl" class="buttons">
            <button id="symbol-add-button" onclick="addSymbol(0);">
                Add
            </button>
          </div>
          <div id="symbol-info-wrap">
            <div id="symbol-info" class="symbol-info">
            </div>
            <div id="symbol-ref-ctrl" class="buttons">
              <button id="symbol-ref-add-button" onclick="addSymbol(1);">
                Add
              </button>
            </div>
            <div id="symbol-ref-info" class="symbol-info">
            </div>
          </div>
        </div>
        <div id="right">
          <div id="dyn-symbol-list" class="symbol-list">
          </div>
        </div>
      </div>
    </div>''', file = output)
    print('  </body>', file = output)
