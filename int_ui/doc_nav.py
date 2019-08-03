from .gen_html import startHtmlPage
#===============================================
def formDocNavigationPage(output, common_title, html_base, ds_h):
    doc_seq = ds_h.getDataInfo().get("doc")
    assert doc_seq is not None
    startHtmlPage(output,
        common_title + "-DOC %s" % ds_h.getName(), html_base,
        css_files = ["doc_nav.css", "base.css"],
        js_files = ["doc_nav.js", "base.js"])

    print('  <body onload="initReportPage(\'%s\', \'%s\');">' %
        (ds_h.getName(), common_title), file = output)
    print('''
    <div id="all">
      <div id="left">
        <div id="doc-list">
        </div>
      </div>
      <div id="right">
        <div id="title">
            <span id="ds-name" onclick="goDS();"></span>:
            <span id="doc-title"></span>
        </div>
        <iframe id="doc-content" name="doc-content">
        </iframe>
      </div>
    </div>''', file = output)
    print('  </body>', file = output)
