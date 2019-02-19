from .gen_html import startHtmlPage

#===============================================
def formXLTreePage(output, title, common_title, html_base, xl_ds):
    startHtmlPage(output, title, html_base,
        css_files = ["base.css", "xltree.css"],
        js_files = ["xltree.js"])

    print >> output, (
        '  <body id="_body" onload="initXL(\'%s\', \'%s\');">' %
        (xl_ds.getName(), common_title))

    _formXLPannel(output, xl_ds.getName())
    _formCurCondDiv(output)
    _formNoteDiv(output)
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
                    <div id="ds-ctrl-home" onclick="goHome();"
                        class="drop ctrl-menu">Home Directory</div>
                    <div id="ds-ctrl-home" onclick="openNote();"
                        class="drop ctrl-menu">Dataset Note</div>
                </div>
            </span>&emsp;
            XL dataset: <span id="xl-name"></span>
        </div>
        <div id="xl-tree-info">
            Accepted: <span id="report-accepted"></span>&emsp;
            Rejected: <span id="report-rejected"></span><br/>
            <!--div id="tree-ctrl">
              <button id="tree-undo" title="Undo"
                onclick='sTreeCtrlH.modify(\"undo\");'> &#8630;
              </button>
              <button id="tree-redo" title="Redo"
                onclick='sTreeCtrl.modify(\"redo\");'> &#8631;
              </button>
            </div-->
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
            <div id="cond-error"></div>
            <div id="cur-cond-numeric">
              <span id="cond-min" class="num-set"></span>
              <input id="cond-min-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-sign" class="num-sign"
                onclick="sOpNumH.checkControls(true);"></span>
              <input id="cond-max-inp" class="num-inp"
                type="text" onchange="sOpNumH.checkControls();"/>
              <span id="cond-max" class="num-set"></span>
              <span id="num-count" class="num-count"></span>
              <input id="cond-undef-check" class="num-inp"
                type="checkbox"  onchange="sOpNumH.checkControls();"/>
              <span id="cond-undef-count" class="num-count"></span>
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
                        onchange="sOpEnumH.checkControls(1);"/>&nbsp;AND
                    </span><br/>
                    <span id="cond-mode-not-span">
                      <input id="cond-mode-not" type="checkbox"
                        onchange="sOpEnumH.checkControls(3);"/>&nbsp;NOT
                    </span><br/>
                    <span id="cond-mode-only-span">
                      <input id="cond-mode-only" type="checkbox"
                        onchange="sOpEnumH.checkControls(2);"/>&nbsp;ONLY
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div id="cond-ctrl">
                <button id="cond-button-set" onclick="fixCond();">
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
def _formNoteDiv(output):
    print >> output, '''
    <div id="note-back">
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
        </div>
      </div>
    </div>
'''
#===============================================
def _formSamplesDiv(output):
    pass
