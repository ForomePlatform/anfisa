import numbers, logging
from StringIO import StringIO

#===============================================
class ObjectAttributeChecker:

    @classmethod
    def check(cls, view_setup, data_objects, dataset_name):
        checker = cls(view_setup.getAspects(),
                view_setup.configOption("attrs.to.ignore"))
        for obj in data_objects:
            checker.checkObj(obj)
        if not checker.finishUp():
            report = StringIO()
            print >> report, "Errors in DataRecord_AJson %s" % dataset_name
            checker.reportBadAttributes(report)
            logging.error(report.getvalue())
        else:
            logging.warning("Attrs are all set for DataRecord_AJson %s"
                % dataset_name)

    def __init__(self, aspects, ignore_attrs):
        self.mGoodAttrs = set()
        self.mBadAttrs = set()
        for attr in ignore_attrs:
            self.mGoodAttrs.add(attr)
        for asp in aspects:
            asp._feedAttrPath(self.mGoodAttrs)

    def checkObj(self, obj, path = ""):
        if path and path not in self.mGoodAttrs:
            self.mBadAttrs.add(path)
            return
        if obj is None:
            return
        if isinstance(obj, basestring) or isinstance(obj, numbers.Number):
            return
        elif isinstance(obj, dict):
            for a_name, sub_obj in obj.items():
                self.checkObj(sub_obj, path + '/' + a_name)
        elif isinstance(obj, list):
            for sub_obj in obj:
                self.checkObj(sub_obj, path + "[]")
        else:
            logging.error("BAD:path=%s: %r" % (path, obj))
            self.mBadAttrs.add(path + "?")

    def finishUp(self):
        if len(self.mBadAttrs) > 0:
            good_path_heads = set()
            for path in self.mGoodAttrs:
                if path.endswith('*'):
                    good_path_heads.add(path[:-1])
            ign_path_set = set()
            for bad_path in self.mBadAttrs:
                if bad_path.startswith('/_'):
                    ign_path_set.add(bad_path);
                    continue
                for path in good_path_heads:
                    if (bad_path.startswith(path) and
                            bad_path[len(path):][:1] in '/['):
                        ign_path_set.add(bad_path)
                        break
            self.mBadAttrs -= ign_path_set
        return len(self.mBadAttrs) == 0

    def reportBadAttributes(self, output):
        print >> output, ("Bad attribute path list(%d):" %
            len(self.mBadAttrs))
        for path in sorted(self.mBadAttrs):
            print >> output, "\t%s" % path
