from datetime import datetime, timedelta
from xml.sax.saxutils import escape

#===============================================
def startHtmlReport(output, title = None, use_pygments = False):
    print('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">''',
    file = output)
    if title:
        print('    <title>%s</title>' % escape(title), file = output)
    print('    <link rel="stylesheet" href="report.css" '
        'type="text/css" media="all"/>', file = output)
    if use_pygments:
        print('    <link rel="stylesheet" href="py_pygments.css" '
            'type="text/css" media="all"/>', file = output)

    print('  </head>', file = output)

#===============================================
def reportDS(ds_data, output):
    startHtmlReport(output, "Anfisa dataset %s report" % ds_data["name"],
        "receipt" in ds_data and ds_data["receipt"].get("kind") == "tree")
    print('  <body>', file = output);
    print('    <table class="report-main">', file = output);
    for key, title in [
            ("name", "Name"),
            ("kind", "Kind"),
            ("count", "Variants"),
            ("date-created", "Created at"),
            ("date-reloaded", "Reloaded at"),
            ("base-ds", "Base dataset"),
            ("base-count", "Base variants"),
            ("date-base", "Base loaded at")]:
        if ds_data.get(key) is None:
            continue
        val = ds_data[key]
        if key.startswith("date-"):
            dt = datetime.fromisoformat(val)
            val = str(dt - timedelta(microseconds = dt.microsecond))
        else:
            val = str(val)
        print('<tr><td class="rep-title">%s<td>' % escape(title),
            file = output)
        print('<td class="rep-val">%s<td></tr>' % escape(val), file = output)
    print('    </table>', file = output)

    if "src-versions" in ds_data and len(ds_data["src-versions"]) >0:
        print('<h2>Annotation sources versions</h2>', file = output)
        print('<table class="rep-filter">', file = output)
        for name, value in ds_data["src-versions"]:
            print('<tr><td class="anno-src">%s</td>' % escape(name),
                file = output)
            print('<td class="anno-ver">%s</td></tr>' % escape(value),
                file = output)
        print('</table>', file = output)

    if "receipt" in ds_data:
        receipt = ds_data["receipt"]
        if receipt["kind"] == "filter":
            print('<h2>Applied filter</h2>', file = output)
            print('<table class="rep-filter">', file = output)
            for instr in receipt["seq"]:
                print('<tr><td>%s</td></tr>' % escape(instr), file = output)
            print('</table>', file = output)
        else:
            assert receipt["kind"] == "tree"
            print('<h2>Applied tree code</h2>', file = output)
            for key_t, title_t in [
                    ("std", "Based on"),
                    ("version", "Version")]:
                if key not in receipt:
                    continue
                print('<p class="tree-info">%s: %s</p>' %
                    (escape(title_t), escape(receipt[key])), file = output)
            print('<table class="rep-tree">', file = output)
            for instr, count, ret_mode in receipt["points"]:
                print('<tr><td class="tree-point">%s</td>' % escape(instr),
                    file = output)
                if count is None:
                    print('<td></td>' % count, file = output)
                elif ret_mode:
                    print('<td class="point-ok">+%d</td>' % count,
                        file = output)
                elif ret_mode is False:
                    print('<td class="point-drop">-%d</td>' % count,
                        file = output)
                else:
                    print('<td class="point-ign">%d</td>' % count,
                        file = output)
            print('</table>', file = output)

    print('  </body>', file = output);
    print('</html>', file = output);
