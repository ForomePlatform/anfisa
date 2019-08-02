from .gen_html import startHtmlPage, formFilterPannel

#===============================================
def formXLPage(output, common_title, html_base, xl_ds, ws_url):
    startHtmlPage(output, common_title + "-XL " + xl_ds.getName(), html_base,
        css_files = ["base.css", "xl.css"],
        js_files = ["xl.js", "filters.js",
            "fctrl.js", "xl_ctrl.js", "base.js"])

    print('  <body onload="setupXLFilters(\'%s\', \'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title, ws_url), file = output)

    _formXLPannel(output, xl_ds.getName())
    formNoteDiv(output)
    formCreateWsDiv(output)
    formSubViewDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formXLPannel(output, ds_name):
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
                    <div onclick="goToPage(\'TREE\');"
                        class="drop ctrl-menu">Decision tree panel</div>
                    <div onclick="openNote();"
                        class="drop ctrl-menu">Dataset Note...</div>
                    <div onclick="showExport();"
                        class="drop ctrl-menu" >Export...</div>
                    <div onclick="wsCreate();"
                        class="drop ctrl-menu">Create workspace...</div>
                </div>
                <div id="export-result" class="drop"></div>
            </span>&emsp;
            XL dataset: <span id="xl-name"></span><br/>
            Records: <span id="list-report"></span>
        </div>
        <div id="xl-list">
            <button id="xl-sub-view"
                onclick="sSubViewH.show()">View variants</button>
        </div>
      </div>''', file = output)
    formFilterPannel(output)

#===============================================
def formNoteDiv(output):
    print('''
    <div id="note-back" class="modal-back">
      <div id="note-mod">
        <div id="note-top">
            <p id="note-title">Dataset
                <span id="note-ds-name"></span> note
              <span class="close-it" onclick="sViewH.modalOff();">&times;</span>
            </p>
        </div>
        <div id="work-note-area">
            <textarea id="note-content"></textarea>
        </div>
        <div id="work-note-ctrl">
              <button onclick="saveNote();">
                Save
              </button>
              <button onclick="sViewH.modalOff();">
                Done
              </button>
              <span id="note-time"></span>
            </div>
          </div>
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
              <span class="close-it" onclick="sViewH.modalOff();">&times;</span>
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
      <div id="sub-view-mod">
        <div id="sub-view-left">
            <div id="sub-view-ctrl">
                <span id="sub-view-list-report"></span><br/>
                <input id="sub-view-check-full" type="checkbox"
                    onchange="sSubViewH.setMode(0);"/>
                <span id="sub-view-mod-full">Full list</span><br/>
                <input id="sub-view-check-samples" type="checkbox"
                    onchange="sSubViewH.setMode(1);"/>
                <span id="sub-view-mod-samples">Samples-25</span><br/>
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
