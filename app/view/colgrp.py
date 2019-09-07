from bitarray import bitarray
#===============================================
class ColGroupsH:
    def __init__(self, attr_title_pairs = None,
            attr = None, title = None):
        self.mATPairs = attr_title_pairs
        self.mHitGroup = None
        if attr is not None:
            assert self.mATPairs is None
            self.mATPairs  = [(attr, title)]
        else:
            assert self.mATPairs is not None

    def setHitGroup(self, group_attr):
        for idx, pair in enumerate(self.mATPairs):
            if pair[0] == group_attr:
                self.mHitGroup = idx
                return
        assert False, "Failed to set view hit group"

    def getSize(self):
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
    def formColumns(self, in_objects, details = None):
        assert len(in_objects) == 1
        rec_obj = in_objects[0]
        prefix_head = []
        objects = []
        hit_columns = None
        if details and self.mHitGroup is not None:
            hit_columns = set()
        group_idx = -1
        for attr, title in self.mATPairs:
            group_idx += 1
            if attr not in rec_obj:
                continue
            seq = rec_obj[attr]
            if len(seq) == 0:
                continue
            rep_count = "[%d]" % len(seq)
            if hit_columns is not None and self.mHitGroup == group_idx:
                it_map = bitarray(details)
                for idx in range(len(seq)):
                    if it_map[idx]:
                        hit_columns.add(idx + len(objects))
                if len(hit_columns) != len(seq):
                    rep_count = "[%d/%d]" % (len(hit_columns), len(seq))
            objects += seq
            if title:
                title += rep_count
            prefix_head.append((title, len(seq)))
        if len(prefix_head) == 1 and prefix_head[0][0] is None:
            prefix_head = None
        return objects, prefix_head, hit_columns
