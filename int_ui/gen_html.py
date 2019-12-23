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
def formWsPage(output, common_title, html_base, workspace, ws_pub_url):
    startHtmlPage(output,
        common_title + "-WS " + workspace.getName(), html_base,
        css_files = ["base.css", "vrec.css", "anf.css",
            "filters.css", "zones.css"],
        js_files = ["anf.js", "monitor.js", "fctrl.js", "base.js",
            "filters.js", "zones.js"])

    print('  <body onload="initWin(\'%s\', \'%s\');">' %
        (workspace.getName(), common_title), file = output)
    _formMainDiv(output, workspace.getName(), ws_pub_url)
    print('    <div id="filter-back">', file = output)
    formFilterPanel(output)
    print('    </div>', file = output)
    _formZonesDiv(output, workspace.iterZones())
    formNoteDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formMainDiv(output, workspace_name, ws_pub_url):
    print('''
    <div id="top">
        <div id="top-ws">
            <div class="dropdown">
                <span id="control-open">&#8285;</span>
                <div id="control-menu" class="dropdown-content">
                    <a class="drop" onclick="goHome();"
                        >Home Directory</a>
                    <a class="drop" onclick="goToPage(\'DOC\');"
                      id="menu-doc">Documentation</a>
                    <a class="drop" onclick="goToPage(\'DTREE\');"
                        >Decision tree panel</a>
                    <a class="drop" onclick="openNote();"
                        >Dataset Note...</a>
                    <a class=:drop" onclick="showExport();"
                        >Export...</a>
                </div>
                <div id="export-result" class="drop"></div>
            </div> <span id="ds-name" class="bold"></span>
            <div class="nomargins">
                Variants:&nbsp;<span id="ws-list-report" class="bold"
                ></span>
            </div>
            <div class="nomargins">
                <small>
                  Transcripts:&nbsp;<span id="ws-transcripts-report"></span>
                </small>
              </div>
        </div>
        <div  id="top-filters">
          Filters:
          <div id="flt-ctrl">
            <div id="flt-named">
              <input id="flt-check-named" type="checkbox"
                onchange="checkCurFilters(0);"/>
              <select id="flt-named-select" onchange="pickNamedFilter();">
                <option value=""></option>
              </select>
            </div>
            <div id="flt-cur">
              <input id="flt-check-current" type="checkbox"
                onchange="checkCurFilters(1);"/>
              <span id="flt-current-state" title="Setup filter"
                 onclick="filterModOn();">
              </span>
            </div>
          </div>
        </div>
        <div id="top-zones">
          <div id="zone-ctrl">
            Zone:
              <span id="zone-cur-title"></span>
              <select style="visibility:hidden;">
                <option value=""></option>
              </select>
          </div>
          <div id="zone-cur">
            <input id="zone-check" type="checkbox"
                onchange="checkCurZone();"/>
            <span id="zone-descr" onclick="zoneModOn();"></span>
          </div>
         </div>
         <div id="top-tags">
            <div id="tags-ctrl">
              Tags:
              <select id="cur-tag" onchange="pickTag();">
                <option value=""></option>
              </select>
              <span id="cur-tag-count"></span>
            </div>
            <div id="cur-tag-nav">
              <span id="cur-tag-nav-first" class="tags-nav"
                onclick="tagNav(0);">|&#9664;</span>
              <span id="cur-tag-count-prev" class="tags-count"></span>
              <span id="cur-tag-nav-prev" class="tags-nav"
                onclick="tagNav(1);">&#9664;</span>
              <span id="cur-tag-here">&#11044;</span>
              <span id="cur-tag-nav-next" class="tags-nav"
                onclick="tagNav(3);">&#9654;</span>
              <span id="cur-tag-count-next" class="tags-count"></span>
              <span id="cur-tag-nav-last" class="tags-nav"
                onclick="tagNav(4);">&#9654;|</span>
            </div>
         </div>
         <div id="top-ref">
            <a class="ext-ref" href="%(ws_pub_url)s?ds=%(ws)s"
                target="blank" title="To front end">&#x23f5;</a>
        </div>
      </div>
      <div id="bottom">
        <div id="bottom-left">
          <div id="wrap-rec-list">
            <div id="rec-list">
            </div>
          </div>
        </div>
        <div id="bottom-right">
            <iframe id="rec-frame2" name="rec-frame2" src="norecords">
            </iframe>
            <iframe id="rec-frame1" name="rec-frame1" src="norecords">
            </iframe>
        </div>
    </div>''' % {"ws": workspace_name, "ws_pub_url": ws_pub_url},
    file = output)

#===============================================
def _formZonesDiv(output, zones):
    rep_check_zones, rep_div_zones = [], []
    for zone_h in zones:
        zone_check_id = "zn-check--%s" % zone_h.getName()
        rep_check_zones.append(('<span id="zn--%s">'
            '<input id="%s" class="zone-checkbox" type="checkbox" '
            'onchange="checkWorkZone(\'%s\');"/>'
            '<label for="%s">%s</label></span>') %
            (zone_h.getName(), zone_check_id, zone_h.getName(),
            zone_check_id, escape(zone_h.getTitle())))
        rep_div_zones.append('<div class="work-zone-list" '
            'id="zn-div--%s"></div>' % zone_h.getName())
    params = {
        "check_zones": "\n".join(rep_check_zones),
        "div_zones": "\n".join(rep_div_zones)}

    print('''
    <div id="zone-back">
      <div id="zone-mod">
        <div id="zone-top">
            <p id="zone-title">Zone setup
              <span class="close-it" onclick="relaxView();">&times;</span>
            </p>
        </div>
        <div id="work-zone-area">
          <div id="work-zone-left">
            <div id="work-zone-kind">
               %(check_zones)s
            </div>
            <div id="work-zone-wrap-list">
                %(div_zones)s
            </div>
          </div>
          <div id="zone-right">
            <div id="work-zone-wrap-def">
                <div id="work-zone-def">
                </div>
            </div>
            <div id="work-zone-ctrl">
              <button class="op-button"
                  onclick="relaxView();">
                Done
              </button>
              <button id="work-zone-clear" class="op-button"
                  onclick="zoneClearSelect();">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
''' % params, file = output)

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
      </div>
    </div>
''', file = output)

#===============================================
def tagsBlock(output):
    print('''
<div id="tg-all">
  <div id="tg-wrap-filters">
    <div id="tg-filters">
        <i>Filters:</i> <span id="tg-filters-list"></span>
    </div>
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
        <button id="tg-tag-undo" class="op-button" title="Undo"
            onclick="tagEnvUndo();">
          &#8630;
        </button>
        <button id="tg-tag-redo" class="op-button"  title="Redo"
            onclick="tagEnvRedo();">
          &#8631;
        </button>
        <span id="tags-time">
        </span>
      </div>
    </div>
  </div>
</div>''', file = output)

#===============================================
def noRecords(output):
    startHtmlPage(output, css_files = ["anf.css"])
    print('''
  <body>
    <h3>No variants available</h3>
    <p>Try to drop <button onclick='parent.window.updateCurZone(false);'
            >zone</button>
        or
        <button onclick='parent.window.updateCurFilter("");'
            >filter</button>.</p>
  </body>
</html>''', file = output)

#===============================================
def dirPage(output, common_title, html_base, ws_pub_url):
    startHtmlPage(output, common_title + " home", html_base,
        css_files = ["dir.css"], js_files = ["dir.js", "base.js"])
    print('''
  <body onload="setup(\'%s\', \'%s\');">
    <h2>%s home directory</h2>
    <p id="p-version">System version: <span id="span-version"></span></p>
    <div id="div-main">
    </div>
  </body>
</html>''' % (common_title, ws_pub_url, common_title), file = output)

#===============================================
def notFound(output, common_title, html_base):
    startHtmlPage(output, common_title + ": Page not found",
        html_base, css_files = ["dir.css"])
    print('''
  <body>
    <h2>Page not found</h2>
    <p><a href="dir" target="%s">Anfisa home</a></p>
  </body>
</html>''' % (common_title + "/dir"), file = output)

#===============================================
def formFilterPanel(output):
    print('''
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
            <span id="close-filter" class="close-it"
                onclick="relaxView();">&times;</span>
          </div>
          <div id="cur-cond-message">
          </div>
          <div id="filter-cur-cond">
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
              <div id="wrap-cond-enum">
                <div id="wrap-cond-enum-list">
                  <div id="cur-cond-enum-list">
                     <div id="op-enum-list">
                     </div>
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
            <div id="cur-cond-import">
                <span "cur-import-status">Import</span>
            </div>
            <div id="cur-cond-loading">
               <div class="loading">Loading data...</div>
            </div>
          </div>
          <div id="filters-edit-ctrl">
            <button class="op-button drop" id="filter-clear-all-cond"
                onclick='sOpFilterH.modify(\"clear-all\");'>
                Clear
            </button>
            <div class="dropdown">
              <button class="op-button drop">
                Filters...
              </button>
              <div id="filters-op-list" class="dropdown-content">
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
