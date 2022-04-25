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
from .gen_html import startHtmlPage
#===============================================
def formGenesPage(output, common_title, html_base, ds_h):
    startHtmlPage(output,
        common_title + "-Genes %s" % ds_h.getName(), html_base,
        css_files = ["genes.css", "base.css"],
        js_files = ["genes.js", "base.js"])

    print(f'  <body onload="initGenesPage(\'{ds_h.getName()}\', '
        f'\'{ds_h.getDSKind()}\', \'{common_title}\');">', file = output)
    print('''
    <div id="all">
      <div id="left">
        <div id="gene-ctrl">
          <div id="sel-panel">
            <input id="sel-check-panel" type="checkbox"
                onchange="checkSel(0);"/>
           Panels: <br/>
            <select id="panel-select" onchange="pickPanel();">
                <option value=""></option>
            </select>
          </div>
          <div id="sel-pattern">
            <input id="sel-check-pattern" type="checkbox"
                onchange="checkSel(1);"/>
            Pattern: <br/>
            <input id="pattern-input" type="text" onchange="pickPattern();"/>
            <button id="pattern-find" class="op-button" onclick="pickPattern();">
                Find
            </button>
          </div>
          <div id="sel-options">
          </div>
        </div>
        <div id="symbol-list">
        </div>
      </div>
      <div id="right">
        <div id="symbol-info">
        </div>
      </div>
    </div>''', file = output)
    print('  </body>', file = output)
