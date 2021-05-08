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

from .gen_html import startHtmlPage
#===============================================
def dirPage(output, common_title, html_base, ws_pub_url, doc_sets):
    startHtmlPage(output, common_title + " home", html_base,
        css_files = ["dir.css", "base.css"], js_files = ["dir.js", "base.js"])

    doc_sets_repr = []
    for doc_set in doc_sets:
        doc_url = doc_set.getUrl()
        doc_title = escape(doc_set.getTitle())
        doc_sets_repr.append(f'<li><a href="{doc_url}" '
            f'target="{common_title}-DOC">{doc_title}</a>')

    print(f'<body onload="setup(\'{common_title}\', \'{ws_pub_url}\');">', file = output)
    print('''
        <h2>%(common_title)s home directory</h2>
        <div id="dir-main">
           <div id="dir-list"></div>
           <div id="dir-info">
                <div id="div-version">
                    System version:&nbsp;<span id="app-version"</span>
                </div>
                <div id="ds-info"></div>
           </div>
        </div>
        <div id="dir-docs">
          <ul>
            %(doc_sets_repr)s
          </ul>
        </div>
      </body>
    </html>''' % {
    "common_title": common_title,
    "doc_sets_repr": doc_sets_repr}, file = output)

#===============================================
def subdirPage(output, common_title, html_base, ws_url, ds_h):
    startHtmlPage(output,
        common_title + " " + ds_h.getName() + " subdirectory", html_base,
        css_files = ["dir.css"], js_files = ["dir.js", "base.js"])

    print(f'<body onload="setupSubDir(\'{common_title}\', \'{ws_url}\', '
        f'\'{ds_h.getName()}\');">', file = output)
    print(f'<h2>Dataset {ds_h.getName()} directory</h2>', file = output)
    print('''
            <div id="dir-main">
               <div id="dir-list"></div>
               <div id="dir-info">
                    <div id="div-version">
                        System version:&nbsp;<span id="app-version"</span>
                    </div>
                    <div id="ds-info"></div>
               </div>
            </div>
          </body>
        </html>''', file = output)

#===============================================
def notFound(output, common_title, html_base):
    startHtmlPage(output, common_title + ": Page not found",
        html_base, css_files = ["base.css"])
    print('''
  <body>
    <h2>Page not found</h2>
    <p><a href="dir" target="%s">Anfisa home</a></p>
  </body>
</html>''' % (common_title + "/dir"), file = output)

#===============================================
def noRecords(output):
    startHtmlPage(output, css_files = ["base.css"])
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
