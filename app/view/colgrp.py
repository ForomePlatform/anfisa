#===============================================
class ColGroupsH:
    def __init__(self, attr_title_pairs = None,
            attr = None, title = None):
        self.mATPairs = attr_title_pairs
        if attr is not None:
            assert self.mATPairs is None
            self.mATPairs  = [(attr, title)]
        else:
            assert self.mATPairs is not None

    def getCount(self):
        return len(self.mATPairs)

    def getAttr(self, idx):
        return self.mATPairs[idx][0]

    def getTitle(self, idx):
        return self.mATPairs[idx][1]

    def getAttrNames(self):
        return [attr for attr, title in self.mATPairs]

    #=============================
    def dump(self):
        return [[attr, title] for attr, title in self.mATPairs]

    @classmethod
    def load(cls, data):
        if data is None:
            return None
        return cls(attr_title_pairs = data)

    #=============================
    def formColumns(self, in_objects):
        assert len(in_objects) == 1
        rec_obj = in_objects[0]
        prefix_head = []
        objects = []
        for attr, title in self.mATPairs:
            if attr not in rec_obj:
                continue
            seq = rec_obj[attr]
            if len(seq) == 0:
                continue
            objects += seq
            prefix_head.append((title, len(seq)))
        if len(prefix_head) == 1 and prefix_head[0][0] is None:
            prefix_head = None
        return objects, prefix_head
