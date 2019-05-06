from xml.sax.saxutils import escape

from .gen_html import startHtmlPage
from app.filter.code_works import StdTreeCodes
#===============================================
def formXLTreePage(output, title, common_title, html_base, xl_ds, ws_url):
    startHtmlPage(output, title, html_base,
        css_files = ["xltree.css", "py_pygments.css", "base.css"],
        js_files = ["xltree.js", "fctrl.js", "flt.js"])

    print >> output, (
        '  <body onload="initXL(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_url))

    _formXLPannel(output, xl_ds.getName())
    _formCurCondDiv(output)
    _formVersionsDiv(output)
    _formNoteDiv(output)
    _formCreateWsDiv(output)
    _formEditCodeDiv(output)
    _formSamplesDiv(output)

    print >> output, ' </body>'
    print >> output, '</html>'

#===============================================
def _formXLPannel(output, ds_name):
    print >> output, '''
      <div id="xl-ctrl">
        <div id="xl-info">
            <span id="ds-control-wrap" title="Control Menu..." class="drop">
                <span id="ds-control-open" class="drop"
                    onclick="openControlMenu();">&#8285;</span>
                <div id="ds-control-menu" class="drop">
                    <div onclick="goHome();"
                        class="drop ctrl-menu">Home Directory</div>
                    <div onclick="goToFilters();"
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
                <option value="">in work</option>'''
    for std_name in StdTreeCodes.getKeys():
        print >> output, '                <option value="%s">%s</option>' % (
            escape(std_name), escape(std_name))
    print >> output, '''
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
            Records in scope: <span id="list-report"></span>
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
      </div>'''

#===============================================
def _formCurCondDiv(output):
    print >> output, '''
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
                    Show zeros&nbsp;<input id="cur-enum-zeros" type="checkbox"
                        onchange="sOpEnumH.careEnumZeros();"/>
                  </div>
                  <div id="cur-cond-enum-mode">
                    <span id="cond-mode-and-span">
                      <input id="cond-mode-and" type="checkbox"
                        onchange="sOpEnumH.checkControls(1);"/>&nbsp;all
                    </span><br/>
                    <span id="cond-mode-not-span">
                      <input id="cond-mode-not" type="checkbox"
                        onchange="sOpEnumH.checkControls(3);"/>&nbsp;not
                    </span><br/>
                    <span id="cond-mode-only-span">
                      <input id="cond-mode-only" type="checkbox"
                        onchange="sOpEnumH.checkControls(2);"/>&nbsp;only
                    </span>
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
    </div>'''

#===============================================
def _formVersionsDiv(output):
    print >> output, '''
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
'''

#===============================================
def _formNoteDiv(output):
    print >> output, '''
    <div id="note-back" class="modal-back">
      <div id="note-mod">
        <div id="note-top">
            <p id="note-title">Dataset
                <span id="note-ds-name"></span> note
              <span class="close-it" onclick="modalOff();">&times;</span>
            </p>
        </div>
        <div id="work-note-area">
            <textarea id="note-content"></textarea>
        </div>
        <div id="work-note-ctrl">
            <button onclick="saveNote();">
              Save
            </button>
            <button onclick="modalOff();">
              Done
            </button>
            <span id="note-time"></span>
        </div>
      </div>
    </div>
'''

#===============================================
def _formCreateWsDiv(output):
    print >> output, '''
    <div id="create-ws-back" class="modal-back">
      <div id="create-ws-mod">
        <div id="create-ws-top">
            <span id="create-ws-title"></span>
              <span class="close-it" onclick="modalOff();">&times;</span>
        </div>
        <div id="create-ws-main">
            <div>Workspace name:
                <input id="create-ws-name" type="text"/>
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
'''

#===============================================
def _formEditCodeDiv(output):
    print >> output, '''
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
'''

#===============================================
def _formSamplesDiv(output):
    pass
