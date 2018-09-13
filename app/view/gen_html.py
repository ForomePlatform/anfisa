from xml.sax.saxutils import escape

#===============================================
def formTopPage(output, title, html_base,
        workspace_name, modes, zones):
    params = {
        "title": title,
        "workspace": workspace_name,
        "modes": modes,
        "html-base": (' <base href="%s" />' % html_base) if html_base else ""}
    print >> output, '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>%(title)s</title>
    %(html-base)s
    <link rel="stylesheet" href="base.css" type="text/css" media="all"/>
    <link rel="stylesheet" href="anf.css" type="text/css" media="all"/>
    <link rel="stylesheet" href="filters.css" type="text/css" media="all"/>
    <link rel="stylesheet" href="zones.css" type="text/css" media="all"/>
    <link rel="stylesheet" href="rules.css" type="text/css" media="all"/>
    <script type="text/javascript" src="anf.js"></script>
    <script type="text/javascript" src="monitor.js"></script>
    <script type="text/javascript" src="filters.js"></script>
    <script type="text/javascript" src="conditions.js"></script>
    <script type="text/javascript" src="zones.js"></script>
    <script type="text/javascript" src="rules.js"></script>
  </head>
  <body onload="initWin(\'%(workspace)s\', \'%(modes)s\');">''' % params

    _formMainDiv(output, workspace_name)
    _formFiltersDiv(output)
    _formZonesDiv(output, zones)
    _formRulesDiv(output)

    print >> output, '''
  </body>
</html>'''

#===============================================
def _formMainDiv(output, workspace_name):
    print >> output, '''
    <div id="all">
      <div id="top">
        <div id="top-ws">
          <div id="ws-ctrl">
            <div id="ws-info">
              Workspace:
              <span id="ws-name"></span><br/>
              <span id="ws-export-wrap" title="Export..." class="drop">
                <span id="ws-export-open" class="drop"
                    onclick="openExport()";>&#11123;</span>
                <div id="ws-export" class="drop">
                    <div id="ws-export-descr" class="drop"></div>
                    <div id="ws-export-result" class="drop"></div>
                </div>
              </span>
            </div>
            <div id="list-info">
              <span id="list-report"></span>
              <input id="list-rand-portion" type="number" min="1" max="5"
                onchange="listRandPortion();"/>
            </div>
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
      </div>
    </div>''' % {"ws": workspace_name}

#===============================================
def _formFiltersDiv(output):
    print >> output, '''
    <div id="filter-back">
      <div id="filter-mod">
        <div id="filter-stat">
          <div id="stat-list">
          </div>
        </div>
        <div id="filter-conditions">
          <div id="filter-ctrl">
            <span id="cond-title"></span>
            <button id="filter-add-cond" onclick="filterAddCond();">
              Add
            </button>
            <button id="filter-update-cond" onclick="filterUpdateCond();">
              Update
            </button>
            <button id="filter-delete-cond"
                onclick="filterDeleteCond();">
              Delete
            </button>
            <button id="filter-undo-cond" title="Undo"
                onclick="filterUndoCond();">
              &#8630;
            </button>
            <button id="filter-redo-cond" title="Redo"
                onclick="filterRedoCond();">
              &#8631;
            </button>
            <span id="close-filter" onclick="filterModOff();">&times;</span>
          </div>
          <div id="filter-cur-cond-text">
            <span id="cond-text"></span>
            <span id="cond-error"></span>
          </div>
          <div id="filter-cur-cond">
            <div id="cur-cond-numeric">
              <span id="cond-min" class="num-set"></span>
              <input id="cond-min-inp" class="num-inp"
                type="text" onchange="checkCurCond(\'min\');"/>
              <span id="cond-sign" class="num-sign"
                onclick="checkCurCond(\'sign\');"></span>
              <input id="cond-max-inp" class="num-inp"
                type="text" onchange="checkCurCond(\'max\');"/>
              <span id="cond-max" class="num-set"></span>
              <span id="num-count" class="num-count"></span><br/>
              <input id="cond-undef-check" class="num-inp"
                type="checkbox"  onchange="checkCurCond(\'undef\');"/>
              <span id="cond-undef-count" class="num-count"
                class="num-count"></span>
            </div>
            <div id="cur-cond-enum">
              <div id="wrap-cond-enum">
                <div id="wrap-cond-enum-list">
                  <div id="cur-cond-enum-list">
                     <div id="op-enum-list">
                     </div>
                  </div>
                </div>
                <div id="cur-cond-enum-mode">
                  <span id="cond-mode-and-span">
                    <input id="cond-mode-and" class="num-inp" type="checkbox"
                      onchange="checkCurCond(\'mode-and\');"/>AND
                  </span><br/>
                  <span id="cond-mode-only-span">
                    <input id="cond-mode-only" class="num-inp" type="checkbox"
                      onchange="checkCurCond(\'mode-only\');"/>ONLY
                  </span><br/>
                  <span id="cond-mode-not-span">
                    <input id="cond-mode-not" class="num-inp" type="checkbox"
                      onchange="checkCurCond(\'mode-not\');"/>NOT
                  </span><br/>
                </div>
              </div>
            </div>
          </div>
          <div id="filter-wrap-list-conditions">
            <div id="filter-list-conditions">
              <div id="cond-list">
              </div>
            </div>
          </div>
          <div id="filters-ctrl">
            <button class="op-button"
                onclick="filterModOff();">
                Done
            </button>
            <button id="filter-filters-on" onclick="filterFiltersSwitch();">
              Filters...
            </button>
            <button id="filter-load-flt" class="op-button"
                onclick="filterLoadFilter();">
              Load
            </button>
            <div id="filter-name-combo" class="combobox">
              <select id="filter-name-filter-list"
                  onchange="fltFilterListSel();">
                <option value=""></option>
              <input id="filter-name-filter" type="text" />
              </select>
            </div>
            <button id="filter-create-flt" class="op-button"
                onclick="filterUpdateFilter(0);">
              Create
            </button>
            <button id="filter-modify-flt" class="op-button"
                onclick="filterUpdateFilter(1);">
              Modify
            </button>
            <button id="filter-delete-flt" class="op-button"
                onclick="filterDeleteFilter();">
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>'''

#===============================================
def _formZonesDiv(output, zones):
    rep_check_zones, rep_div_zones = [], []
    for zone in zones:
        rep_check_zones.append(('<span id="zn--%s">'
            '<input id="zn-check--%s" class="zone-checkbox" type="checkbox" '
            'onchange="checkWorkZone(\'%s\');"/>%s</span>') %
            (zone.getName(), zone.getName(), zone.getName(),
            escape(zone.getTitle())))
        rep_div_zones.append('<div class="work-zone-list" '
            'id="zn-div--%s"></div>' % zone.getName())
    params = {
        "check_zones": "\n".join(rep_check_zones),
        "div_zones": "\n".join(rep_div_zones)}

    print >> output, '''
    <div id="zone-back">
      <div id="zone-mod">
        <div id="zone-top">
            <p id="zone-title">Zone setup
              <span id="close-zone" onclick="zoneModOff();">&times;</span>
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
            <div id="work-zone-def">
            </div>
            <div id="work-zone-ctrl">
              <button class="op-button"
                  onclick="zoneModOff();">
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
''' % params

#===============================================
def _formRulesDiv(output):
    print >> output, '''
    <div id="rules-back">
      <div id="rules-mod">
        <div id="rules-top">
            <p id="rules-title">&#9874; Rules evaluation setup
              <span id="close-rules" onclick="rulesModOff();">&times;</span>
            </p>
        </div>
        <div id="rules-main">
          <div id="rules-left">
            <div id="rules-wrap-columns">
              <div id="rules-columns">
              </div>
            </div>
            <div id="rules-wrap-param">
              <div id="hi----param"
                class="rule-item" onclick="rulesItemSel(\'--param\');">
                  Parameters
              </div>
            </div>
          </div>
          <div id="rules-right">
            <div id="rules-wrap-content">
                <textarea id="rule-item-content"></textarea>
            </div>
            <div id="rule-item-ctrl">
                <button id="rule-item-modify" onclick="ruleItemModify();">
                  Apply changes
                </button>
                <button id="rule-item-reset" onclick="ruleItemReset();">
                  Reset changes
                </button>
            </div>
            <div id="rule-item-errors">
            </div"
          </div>
        </div>
      </div>
    </div>'''

#===============================================
def noRecords(output):
    print >> output, '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <link rel="stylesheet" href="anf.css" type="text/css" media="all"/>
  </head>
  <body>
    <h3>No records available</h3>
    <p>Try to drop <button onclick='parent.window.updateCurZone(false);'
            >zone</button>
        or
        <button onclick='parent.window.updateCurFilter("");'
            >filter</button>.</p>
  </body>
</html>'''

#===============================================
def tagsBlock(output):
    print >> output, '''
<div id="tg-all">
  <div id="tg-wrap-filters">
    <div id="tg-filters">
        <i>Filters:</i> <span id="tg-filters-list"></span>
        <span id="tg-run-rules" title="Rules evaluation setup"
            onclick="window.parent.rulesModOn();">&#9874;</span>
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
        <button id="tg-tag-undo" class="op-button" title="Undo"
            onclick="tagEnvUndo();">
          &#8630;
        </button>
        <button id="tg-tag-redo" class="op-button"  title="Redo"
            onclick="tagEnvRedo();">
          &#8631;
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
    </div>
  </div>
</div>'''
