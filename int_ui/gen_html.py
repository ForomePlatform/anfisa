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

from .mirror_dir import MirrorUiDirectory
#===============================================
def startHtmlPage(output, title = None, html_base = None,
        css_files = None, js_files = None):
    print('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">''',
    file = output)
    if title:
        print('    <title>%s</title>' % escape(title), file = output)
    if html_base:
        print('    <base href="%s" />' % html_base, file = output)
    if css_files:
        for name in css_files:
            print('    <link rel="stylesheet" '
                'href="ui/%s" type="text/css" media="all"/>' %
                MirrorUiDirectory.transform(name), file = output)
    if js_files:
        for name in js_files:
            print('    <script type="text/javascript" '
                'src="ui/%s"></script>' %
                MirrorUiDirectory.transform(name), file = output)
    print('  </head>', file = output)

#===============================================
#===============================================
def formNoteDiv(output):
    print('''
    <div id="note-back" class="modal-back">
      <div id="note-mod">
        <div id="note-top">
            <p id="note-title">Dataset
              <span id="note-ds-name"></span> note
              <span class="close-it"
                onclick="relaxView();">&times;</span>
            </p>
        </div>
        <div id="work-note-area">
            <textarea id="note-content"></textarea>
        </div>
        <div id="work-note-ctrl">
            <button onclick="saveNote();">
                Save
            </button>
            <button onclick="relaxView();">
                Done
            </button>
            <span id="note-time"></span>
        </div>
      </div>
    </div>
''', file = output)

#===============================================
def tagsBlock(output):
    print('''
<div id="tg-all">
  <div id="tg-wrap-filters">
  </div>
  <div id="tg-tags">
    <div id="tg-title">
        <i>Tags:</i>
    </div>
    <div id="tg-tags-left">
      <div id="tg-check-tags-list">
      </div>
      <div id="tg-tags-wrap-list">
        <div id="tg-op-tags-list">
        </div>
      </div>
    </div>
    <div id="tg-tags-right">
      <div id="tg-tags-ctrl">
        <div class="combobox">
          <select id="tg-tags-tag-list" onchange="tagEnvTagSel();">
            <option value=""></option>
          </select>
          <input id="tg-tag-name" type="text" />
        </div>
        <button id="tg-tag-new" class="op-button" onclick="tagEnvNew();">
          Add
        </button>
        <button id="tg-tag-save" class="op-button" onclick="tagEnvSave();">
          Save
        </button>
        <button id="tg-tag-cancel" class="op-button" onclick="tagEnvCancel();">
          Cancel
        </button>
        <button id="tg-tag-delete"
            title="Delete tag" class="op-button" onclick="tagEnvDelete();">
          Delete
        </button>
      </div>
      <div id="tg-tag-wrap-value">
        <div id="tg-tag-value">
        </div>
        <div id="tg-tag-edit">
          <textarea id="tg-tag-value-content" />
          </textarea>
        </div>
      </div>
      <div id="tg-tags-ctrl-tags">
        <button id="tg-tag-clear-all" class="op-button"
            onclick="tagEnvClearAll();">
          Clear
        </button>
        <span id="tags-time">
        </span>
      </div>
    </div>
  </div>
</div>''', file = output)

#===============================================
#===============================================
def formFilterPanel(output):
    print('''
    <div id="filter-mod" class="panel-space">
        <div id="filter-stat">
          <div id="stat-list" class="list-items">
          </div>
        </div>
        <div id="filter-conditions">
          <div id="filter-ctrl">
            <span id="cond-title"></span>
            <button id="filter-add-cond"
                onclick='sOpFilterH.modify(\"add\");'> Add
            </button>
            <button id="filter-update-cond"
                onclick='sOpFilterH.modify(\"update\");'> Update
            </button>
            <button id="filter-delete-cond"
                onclick='sOpFilterH.modify(\"delete\");'> Delete
            </button>
            <button id="filter-undo-cond" title="Undo"
                onclick='sOpFilterH.modify(\"undo\");'> &#8630;
            </button>
            <button id="filter-redo-cond" title="Redo"
                onclick='sOpFilterH.modify(\"redo\");'> &#8631;
            </button>
            <span id="close-filter" class="close-it"
                onclick="relaxView();">&times;</span>
          </div>
          <div id="cur-cond-message"></div>
          <div id="filter-cur-cond">''', file = output)

    formCurConditionControls(output)

    print('''
          </div>
          <div id="filters-edit-ctrl">
            <button class="op-button popup" id="filter-clear-all-cond"
                onclick='sOpFilterH.modify(\"clear-all\");'>
                Clear
            </button>
            <div class="dropdown">
              <button class="op-button popup">
                Filters...
              </button>
              <div id="filters-op-list" class="dropdown-content">
                <a class="popup" id="filters-op-load"
                    onclick="sFiltersH.startLoad();">Load</a>
                <a class="popup" id="filters-op-create"
                    onclick="sFiltersH.startCreate();">Create</a>
                <a class="popup"  id="filters-op-modify"
                    onclick="sFiltersH.startModify();">Modify</a>
                <a class="popup"  id="filters-op-delete"
                    onclick="sFiltersH.deleteIt();">Delete</a>
              </div>
            </div>
            <div id="filter-name-combo" class="combobox">
              <select id="filter-name-combo-list"
                  onchange="sFiltersH.select();">
                <option value=""></option>
              <input id="filter-name-input" type="text" />
              </select>
            </div>
            <button id="filter-act-op" class="op-button"
                onclick="sFiltersH.action();">
              ...
            </button>
          </div>
          <div id="filter-wrap-list-conditions">
            <div id="filter-list-conditions">
              <div id="cond-list">
              </div>
            </div>
          </div>
        </div>
    </div>''', file = output)

#===============================================
def formCurConditionControls(output):
    print('''
           <div id="cur-cond-numeric">
              <span id="cond-min" class="num-set"></span>
              <input id="cond-min-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-min-sign" class="num-sign"
                    onclick="sOpNumH.switchSign(0);"></span>
              <span id="cond-num-value">...</span>
              <span id="cond-max-sign" class="num-sign"
                    onclick="sOpNumH.switchSign(1);"></span>
              <input id="cond-max-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-max" class="num-set"></span>
              <span id="num-count" class="num-count"></span>
            </div>
            <div id="cur-cond-enum">
              <div id="cur-cond-func-param"></div>
              <div id="wrap-cond-enum">
                <div id="cur-cond-enum-list">
                    <div id="op-enum-list">
                    </div>
                </div>
                <div id="cur-cond-enum-ctrl">
                  <div id="cur-cond-enum-zeros">
                    <label for"cur-enum-zeros">Show zeros&nbsp;</label><input
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
            </div>''', file = output)

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
            <div>Dataset name:
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
