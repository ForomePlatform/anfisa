from .gen_html import startHtmlPage, formFilterPannel

#===============================================
def formXLPage(output, title, common_title, html_base, xl_ds, ws_url):
    startHtmlPage(output, title, html_base,
        css_files = ["base.css", "xl.css"],
        js_files = ["xl.js", "filters.js",
            "fctrl.js", "flt.js", "xl_ctrl.js"])

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
      </div>'''
    formFilterPannel(output)

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
