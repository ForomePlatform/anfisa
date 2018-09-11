from xml.sax.saxutils import escape

#===============================================
class AspectH:
    def __init__(self, name, title, path, attrs = None,
            ignored = False, kind = None, col_groups = None,
            expert_only = False):
        self.mName     = name
        self.mTitle    = title
        self.mPath     = path
        self.mAttrs = attrs
        self.mIgnored  = ignored
        self.mExpertOnly = expert_only
        self.mKind = kind if kind else "norm"
        self.mColGroups = col_groups
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

    def checkExpertBlock(self, expert_mode):
        return (not expert_mode) and self.mExpertOnly

    def getAspectKind(self):
        return self.mKind

    def setRecommendedAttrs(self, attrs):
        self.mAttrs = attrs

    def _feedAttrPath(self, registry):
        path_seq = [self.mPath]
        if self.mPath:
            registry.add(self.mPath)
        if self.mColGroups is not None:
            path_seq = []
            for idx in range(self.mColGroups.getCount()):
                grp_attr = self.mColGroups.getAttr(idx)
                grp_path = self.mPath + '/' + grp_attr
                registry.add(grp_path)
                grp_path += "[]"
                registry.add(grp_path)
                path_seq.append(grp_path)
        for path in path_seq:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)

    def formTable(self, output, rec_obj, expert_mode):
        if len(self.mPath) > 1:
            objects = [rec_obj[self.mPath[1:]]]
        else:
            objects = [rec_obj]
        prefix_head = None
        if self.mColGroups:
            objects, prefix_head = self.mColGroups.prepareObjects(objects)
        if len(objects) == 0:
            return

        fld_data = dict()
        for attr in self.mAttrs:
            if (attr.getName() is None or
                    attr.checkExpertBlock(expert_mode) or
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
            print >> output, '<td class="title">%s</td>' % escape(attr.getTitle())
            for val, class_name in fld_data[attr.getName()]:
                print >> output, '<td class="%s">%s</td>' % (class_name, val)
            print >> output, '</tr>'
        print >> output, '</table>'
