from xml.sax.saxutils import escape

#===============================================
class AspectH:
    def __init__(self, name, title, source, field = "",
            attrs = None, ignored = False, col_groups = None,
            research_only = False):
        self.mName     = name
        self.mTitle    = title
        self.mSource   = source
        self.mField    = field
        self.mAttrs = attrs
        self.mIgnored  = ignored
        self.mResearchOnly = research_only
        self.mColGroups = col_groups
        assert self.mSource in ("view", "data")
        if self.mIgnored and self.mAttrs is None:
            self.mAttrs = []

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return self.mAttrs

    def isIgnored(self):
        return self.mIgnored

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getAspectKind(self):
        return {"view": "norm", "data": "tech"}[self.mSource]

    def setRecommendedAttrs(self, attrs):
        self.mAttrs = attrs

    def _feedAttrPath(self, registry):
        path_seq = ['/' + self.mSource]
        registry.add(path_seq[0])
        if self.mField:
            path_seq[0] += '/' + self.mField
            registry.add(path_seq[0])
        if self.mColGroups is not None:
            grp_path_seq = []
            for idx in range(self.mColGroups.getCount()):
                grp_attr = self.mColGroups.getAttr(idx)
                grp_path_seq.append(path_seq[0][:])
                grp_path_seq[-1] += '/' + grp_attr
                registry.add(grp_path_seq[-1])
                grp_path_seq[-1] += '[]'
                registry.add(grp_path_seq[-1])
            path_seq = grp_path_seq
        for path in path_seq:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)

    def formTable(self, output, rec_obj, research_mode):
        objects = [rec_obj[self.mSource]]
        if self.mField:
            objects = [objects[0][self.mField]]
        prefix_head = None
        if self.mColGroups:
            objects, prefix_head = self.mColGroups.prepareObjects(objects)
        if len(objects) == 0:
            return

        fld_data = dict()
        for attr in self.mAttrs:
            if (attr.getName() is None or
                    attr.checkResearchBlock(research_mode) or
                    attr.hasKind("hidden")):
                continue
            values = [attr.getHtmlRepr(obj) for obj in objects]
            if not all([vv == ('-', "none") for vv in values]):
                fld_data[attr.getName()] = values

        print >> output, '<table id="rec-%s">' % self.mName
        if prefix_head:
            print >> output, '<tr class="head"><td class="title"></td>'
            for title, count in prefix_head:
                print >> output, ('<td class="title" colspan="%d">%s</td>' %
                    (count, escape(title)))
            print >> output, '</tr>'

        for attr in self.getAttrs():
            if attr.getName() is None:
                print >> output, (
                    '<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                    (len(objects) + 1))
                continue
            if attr.getName() not in fld_data:
                continue
            print >> output, '<tr>'
            print >> output, '<td class="title">%s</td>' % escape(
                attr.getTitle())
            for val, class_name in fld_data[attr.getName()]:
                print >> output, '<td class="%s">%s</td>' % (class_name, val)
            print >> output, '</tr>'
        print >> output, '</table>'
