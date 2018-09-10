from xml.sax.saxutils import escape

#===============================================
def formTopPage(output, title, html_base,
        workspace_name, modes, zones):
    params = {
        "title": title,
        "workspace": workspace_name,
        "modes": modes,
        "html-base": (' <base href="%s" />' % html_base)
            if html_base else ""}
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
    <link rel="stylesheet" href="hot_eval.css" type="text/css" media="all"/>
    <script type="text/javascript" src="anf.js"></script>
    <script type="text/javascript" src="monitor.js"></script>
    <script type="text/javascript" src="filters.js"></script>
    <script type="text/javascript" src="criteria.js"></script>
    <script type="text/javascript" src="zones.js"></script>
    <script type="text/javascript" src="hot_eval.js"></script>
  </head>
  <body onload="initWin(\'%(workspace)s\', \'%(modes)s\');">''' % params

    _formMainDiv(output)
    _formFiltersDiv(output)
    _formZonesDiv(output, zones)
    _formHotEvalDiv(output)

    print >> output, '''
  </body>
</html>'''

#===============================================
def _formMainDiv(output):
    print >> output, '''
    <div id="all">
      <div id="top">
        <div id="top-ws">
          <div id="ws-dropdown" class="dropdown">
            <span class="dropbtn"> &#10247; </span>
             <div id="ws-dropdown-menu" class="dropdown-content">
                <a onclick="doWsExport();">
              Export</a>
            </div>
          </div>
          <div id="ws-ctrl">
            <div id="ws-info">
              Workspace:
              <span id="ws-name"></span><br/>
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
    </div>'''

#===============================================
def _formFiltersDiv(output):
    print >> output, '''
    <div id="filter-back">
      <div id="filter-mod">
        <div id="filter-stat">
          <div id="stat-list">
          </div>
        </div>
        <div id="filter-criteria">
          <div id="filter-ctrl">
            <span id="crit-title"></span>
            <button id="filter-add-crit" onclick="filterAddCrit();">
              Add
            </button>
            <button id="filter-update-crit" onclick="filterUpdateCrit();">
              Update
            </button>
            <button id="filter-delete-crit"
                onclick="filterDeleteCrit();">
              &times;
            </button>
            <button id="filter-undo-crit" title="Undo"
                onclick="filterUndoCrit();">
              &#8630;
            </button>
            <button id="filter-redo-crit" title="Delete"
                onclick="filterRedoCrit();">
              &#8631;
            </button>
            <span id="close-filter" onclick="filterModOff();">&times;</span>
          </div>
          <div id="filter-cur-crit-text">
            <span id="crit-text"></span>
            <span id="crit-error"></span>
          </div>
          <div id="filter-cur-crit">
            <div id="cur-crit-numeric">
              <span id="crit-min" class="num-set"></span>
              <input id="crit-min-inp" class="num-inp"
                type="text" onchange="checkCurCrit(\'min\');"/>
              <span id="crit-sign" class="num-sign"
                onclick="checkCurCrit(\'sign\');"></span>
              <input id="crit-max-inp" class="num-inp"
                type="text" onchange="checkCurCrit(\'max\');"/>
              <span id="crit-max" class="num-set"></span>
              <span id="num-count" class="num-count"></span><br/>
              <input id="crit-undef-check" class="num-inp"
                type="checkbox"  onchange="checkCurCrit(\'undef\');"/>
              <span id="crit-undef-count" class="num-count"
                class="num-count"></span>
            </div>
            <div id="cur-crit-enum">
              <div id="wrap-crit-enum">
                <div id="wrap-crit-enum-list">
                  <div id="cur-crit-enum-list">
                     <div id="op-enum-list">
                     </div>
                  </div>
                </div>
                <div id="cur-crit-enum-mode">
                  <span id="crit-mode-and-span">
                    <input id="crit-mode-and" class="num-inp" type="checkbox"
                      onchange="checkCurCrit(\'mode-and\');"/>AND
                  </span><br/>
                  <span id="crit-mode-only-span">
                    <input id="crit-mode-only" class="num-inp" type="checkbox"
                      onchange="checkCurCrit(\'mode-only\');"/>ONLY
                  </span><br/>
                  <span id="crit-mode-not-span">
                    <input id="crit-mode-not" class="num-inp" type="checkbox"
                      onchange="checkCurCrit(\'mode-not\');"/>NOT
                  </span><br/>
                </div>
              </div>
            </div>
          </div>
          <div id="filter-wrap-list-criteria">
            <div id="filter-list-criteria">
              <div id="crit-list">
              </div>
            </div>
          </div>
          <div id="filters-ctrl">
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
def _formHotEvalDiv(output):
    print >> output, '''
    <div id="hot-eval-back">
      <div id="hot-eval-mod">
        <div id="hot-eval-top">
            <p id="hot-eval-title">&#9874; Hot evaluation setup
              <span id="close-hot-eval" onclick="hotEvalModOff();">&times;</span>
            </p>
        </div>
        <div id="hot-eval-main">
          <div id="hot-eval-left">
            <div id="hot-eval-wrap-columns">
              <div id="hot-eval-columns">
              </div>
            </div>
            <div id="hot-eval-wrap-param">
              <div id="hi----param"
                class="hot-eval-item" onclick="hotItemSel(\'--param\');">
                  Parameters
              </div>
            </div>
          </div>
          <div id="hot-eval-right">
            <div id="hot-eval-wrap-content">
                <textarea id="hot-eval-item-content"></textarea>
            </div>
            <div id="hot-eval-item-ctrl">
                <button id="hot-item-modify" onclick="hotItemModify();">
                  Apply changes
                </button>
                <button id="hot-item-reset" onclick="hotItemReset();">
                  Reset changes
                </button>
            </div>
            <div id="hot-eval-item-errors">
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
    <p>Try to drop <a onclick='parent.window.updateCurZone(false);'>zone</s>
        or
        <a href='parent.window.updateCurFilter("");'>filter</p>.</p>
  </body>
</html>'''

#===============================================
def tagsBlock(output):
    print >> output, '''
<div id="tg-all">
  <div id="tg-wrap-filters">
    <div id="tg-filters">
        <i>Filters:</i> <span id="tg-filters-list"></span>
        <span id="run-hot-eval" title="Hot evaluations"
            onclick="window.parent.hotEvalModOn();">&#9874;</span>
    </div>
  </div>
  <div id="tg-tags">
    <div id="tg-title">
        <i>Tags:</i>
    </div>
    <div id="tg-tags-left">
      <div id="tg-tags-wrap-list">
        <div id="tg-tags-list">
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
          &times;
        </button>
        <button id="tg-tag-undo" class="op-button" title="Undo" onclick="tagEnvUndo();">
          &#8630;
        </button>
        <button id="tg-tag-redo" class="op-button"  title="Redo" onclick="tagEnvRedo();">
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
