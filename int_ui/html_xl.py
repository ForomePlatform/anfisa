from .gen_html import startHtmlPage

#===============================================
def formXLPage(output, title, common_title, html_base, xl_ds, ws_url):
    startHtmlPage(output, title, html_base,
        css_files = ["base.css", "xl.css"],
        js_files = ["xl.js", "flt.js"])

    print >> output, ('  <body onload="initXL(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_url))

    _formXLPannel(output, xl_ds.getName())
    _formNoteDiv(output)
    _formCreateWsDiv(output)
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
                    onclick="openControlMenu()";>&#8285;</span>
                <div id="ds-control-menu" class="drop">
                    <div onclick="goHome();"
                        class="drop ctrl-menu">Home Directory</div>
                    <div onclick="goToTree();"
                        class="drop ctrl-menu">Decision tree panel</div>
                    <div onclick="openNote();"
                        class="drop ctrl-menu">Dataset Note...</div>
                    <div onclick="showExport();"
                        class="drop ctrl-menu" >Export...</div>
                    <div onclick="wsCreate();"
                        class="drop ctrl-menu">Create workspace...</div>
                </div>
                <div id="ws-export-result" class="drop"></div>
            </span>&emsp;
            XL dataset: <span id="xl-name"></span><br/>
            Records: <span id="list-report"></span>
        </div>
      </div>
      <div id="filter-mod">
        <div id="filter-stat">
          <div id="stat-list">
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
            <!--span id="close-filter" onclick="filterModOff();">&times;</span-->
          </div>
          <div id="filter-cur-cond-text">
            <span id="cond-text"></span>
            <span id="cond-message"></span>
          </div>
          <div id="filter-cur-cond">
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
              <div id="wrap-cond-enum">
                <div id="wrap-cond-enum-list">
                  <div id="cur-cond-enum-list">
                     <div id="op-enum-list">
                     </div>
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
                        onchange="sOpEnumH.checkControls(1);"/>&nbsp;All
                    </span><br/>
                    <span id="cond-mode-not-span">
                      <input id="cond-mode-not" type="checkbox"
                        onchange="sOpEnumH.checkControls(3);"/>&nbsp;Not
                    </span><br/>
                    <span id="cond-mode-only-span">
                      <input id="cond-mode-only" type="checkbox"
                        onchange="sOpEnumH.checkControls(2);"/>&nbsp;Only
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div id="filters-ctrl">
            <!--button class="op-button" onclick="filterModOff();">
                Done
            </button-->
            <button id="filter-clear-all-cond" class="op-button"
                onclick='sOpFilterH.modify(\"clear-all\");'>
                Clear
            </button>
            <div class="dropdown">
              <button id="filter-filters-operations" class="op-button drop"
                    onclick="sFiltersH.menu();">
                Filters...
              </button>
              <div id="filters-op-list" class="dropdown-content drop">
                <a class="drop" id="filters-op-load"
                    onclick="sFiltersH.startLoad();">Load</a>
                <a class="drop" id="filters-op-create"
                    onclick="sFiltersH.startCreate();">Create</a>
                <a class="drop"  id="filters-op-modify"
                    onclick="sFiltersH.startModify();">Modify</a>
                <a class="drop"  id="filters-op-delete"
                    onclick="sFiltersH.deleteIt();">Delete</a>
              </div>
            </div>
            <div id="filter-name-combo" class="combobox">
              <select id="filter-name-filter-list"
                  onchange="sFiltersH.select();">
                <option value=""></option>
              <input id="filter-name-filter" type="text" />
              </select>
            </div>
            <button id="filter-flt-op" class="op-button"
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
    </div>'''

#===============================================
def _formNoteDiv(output):
    print >> output, '''
    <div id="note-back" class="modal-back">
      <div id="note-mod">
        <div id="note-top">
            <p id="note-title">Dataset
                <span id="note-ds-name"></span> note
              <span id="close-note" onclick="sViewH.modalOff();">&times;</span>
            </p>
        </div>
        <div id="work-note-area">
            <textarea id="note-content"></textarea>
        </div>
        <div id="work-note-ctrl">
              <button class="op-button"
                  onclick="saveNote();">
                Save
              </button>
              <button class="op-button"
                  onclick="sViewH.modalOff();">
                Done
              </button>
              <span id="note-time"></span>
            </div>
          </div>
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
              <span class="close-it" onclick="sViewH.modalOff();">&times;</span>
        </div>
        <div id="create-ws-main">
            <div>Workspace name:
                <input id="create-ws-name" type="text"/>
                </span>
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
def _formSamplesDiv(output):
    pass
