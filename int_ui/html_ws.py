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

import int_ui.gen_html as gen_html
#===============================================
def formWsPage(output, common_title, html_base, ds_h, ws_pub_url):
    gen_html.startHtmlPage(output,
        common_title + "-WS " + ds_h.getName(), html_base,
        css_files = ["ws.css", "filters.css", "eval.css",
            "zones.css", "vrec.css", "base.css"],
        js_files = ["ws.js", "filters.js", "eval.js", "func.js",
            "zones.js", "base.js"])

    print('  <body onload="initWin(\'%s\', \'%s\', \'%s\');">' %
        (ds_h.getName(), common_title, ws_pub_url), file = output)
    _formPanel(output, ds_h.getName(), ws_pub_url)
    print('    <div id="filter-back">', file = output)
    gen_html.formFilterPanel(output)
    print('    </div>', file = output)
    _formZonesDiv(output, ds_h.iterZones())
    gen_html.formNoteDiv(output)
    gen_html.formCreateWsDiv(output)

    print(' </body>', file = output)
    print('</html>', file = output)

#===============================================
def _formPanel(output, workspace_name, ws_pub_url):
    print('''
    <div id="top">
        <div id="top-ws">
            <div class="dropdown">
                <span id="control-open">&#8285;</span>
                <div id="control-menu" class="dropdown-content">
                    <a class="popup" onclick="goHome();"
                        >Home Directory</a>
                    <a class="popup" onclick="goToPage(\'DOC\');"
                      id="menu-doc">Documentation</a>
                    <a class="popup" onclick="goToPage(\'DTREE\');"
                        >Decision tree panel</a>
                    <a class="popup" onclick="openNote();"
                        >Dataset Note...</a>
                    <a class="popup" onclick="showExport();"
                        >Export...</a>
                    <a class="popup" onclick="wsCreate();"
                        >Create workspace...</a>
                </div>
                <div id="export-result" class="popup"></div>
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
                onchange="sZoneH.checkControls();"/>
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
            'onchange="sZoneH.setWorkZone(\'%s\');"/>'
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
                  onclick="sZoneH.clearSelection();">
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
''' % params, file = output)
