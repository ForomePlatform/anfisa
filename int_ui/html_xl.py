from .gen_html import startHtmlPage

#===============================================
def formXLPage(output, title, html_base, xl_ds):
    startHtmlPage(output, title, html_base,
        css_files = ["base.css", "xl.css"],
        js_files = ["xl.js"])

    print >> output, ('  <body onload="initXL(\'%s\');">' %
        (xl_ds.getName()))

    _formXLPannel(output, xl_ds.getName())
    _formSamplesDiv(output)

    print >> output, ' </body>'
    print >> output, '</html>'

#===============================================
def _formXLPannel(output, ds_name):
    print >> output, '''
      <div id="xl-title">
        <div id="xl-info">
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
            <span id="cond-error"></span>
          </div>
          <div id="filter-cur-cond">
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
                <div id="cur-cond-enum-ctrl">
                  <div id="cur-cond-enum-zeros">
                    Show zeros&nbsp;<input id="cur-enum-zeros" type="checkbox"
                        onchange="sOpEnumH.careEnumZeros();"/>
                  </div>
                  <div id="cur-cond-enum-mode">
                    <span id="cond-mode-or-span">
                      <input id="cond-mode-or" type="checkbox"
                        onchange="sOpEnumH.checkControls(0);"/>&nbsp;OR
                    </span><br/>
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
def _formSamplesDiv(output):
    pass
