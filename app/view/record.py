from .gen_html import tagsBlock
#===============================================
class DataRecord:
    def __init__(self, dataset, json_obj):
        self.mDataset = dataset
        self.mObj = json_obj

    def getObj(self):
        return self.mObj

    def reportIt(self, output, research_mode):
        print >> output, '<div class="r-tab">'
        print >> output, ('<span id="img-wrap" onclick="tabCfgChange();">'
            '<img id="img-tab2" src="images/tab2-exp.png"/></span>')
        aspects_to_show = []
        for aspect in self.mDataset.getViewSetup().getAspects():
            if aspect.isIgnored():
                continue
            if aspect.checkResearchBlock(research_mode):
                continue
            aspects_to_show.append(aspect)
            print >> output, ('<button class="r-tablnk %s" id="la--%s" '
                'onclick="pickAspect(\'%s\')">%s</button>' %
                (aspect.getAspectKind(), aspect.getName(),
                aspect.getName(), aspect.getTitle()))
        tags_asp_name = self.mDataset.getViewSetup().configOption(
            "aspect.tags.name")
        print >> output, ('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            ("tech",  tags_asp_name, tags_asp_name,
            self.mDataset.getViewSetup().textMessage("aspect.tags.title")))
        print >> output, '</div>'

        print >> output, '<div id="r-cnt-container">'
        for aspect in aspects_to_show:
            print >> output, ('<div id="a--%s" class="r-tabcnt">' %
                aspect.getName())
            if aspect.getName() == "input":
                self.reportInput(output)
            else:
                aspect.formTable(output, self.mObj, research_mode)
            print >> output, '</div>'
        print >> output, ('<div id="a--%s" class="r-tabcnt">' %
            tags_asp_name)
        tagsBlock(output)
        print >> output, '</div>'

        print >> output, '</div>'

    def reportInput(self, output):
        if "input" not in self.mObj["data"]:
            print >> output, '<p class="error">No input data</p>'
            return
        print >> output, '<pre>'
        collect_str = ""
        for fld in self.mObj["data"]["input"].split('\t'):
            if len(fld) < 40:
                if len(collect_str) < 60:
                    collect_str += "\t" + fld
                else:
                    print >> output, collect_str[1:]
                    collect_str = "\t" + fld
                continue
            if collect_str:
                print >> output, collect_str[1:]
                collect_str = ""
            for vv in fld.split(';'):
                var, q, val = vv.partition('=')
                if var == "CSQ":
                    print >> output, "==v====SCQ======v========"
                    for idx, dt in enumerate(val.split(',')):
                        ddd = dt.split('|')
                        print >> output, "%d:\t%s" % (idx, '|'.join(ddd[:12]))
                        print >> output, "\t|%s" % ('|'.join(ddd[12:29]))
                        print >> output, "\t|%s" % ('|'.join(ddd[28:33]))
                        print >> output, "\t|%s" % ('|'.join(ddd[33:40]))
                        print >> output, "\t|%s" % ('|'.join(ddd[40:50]))
                        print >> output, "\t|%s" % ('|'.join(ddd[50:]))
                    print >> output, "==^====SCQ======^========"
                else:
                    print >> output, vv
        if collect_str:
            print >> output, collect_str[1:]
            collect_str = ""
