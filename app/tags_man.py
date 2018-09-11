from collections import defaultdict

from zone import ZoneH
#===============================================
class TagsManager(ZoneH):
    def __init__(self, workspace):
        ZoneH.__init__(self, workspace, "_tags");
        self.mTagSets = defaultdict(set)
        self.mIntVersion = 0
        self.mMarkedSet = set()
        self._loadDataSet()

    def getName(self):
        return "_tags"

    def getIntVersion(self):
        return self.mIntVersion

    def getMarkedSet(self):
        return self.mMarkedSet

    def _loadDataSet(self):
        for rec_no, rec_key in self.getWS().getDataSet().enumDataKeys():
            data_obj = self.getWS().getMongoConn().getRecData(rec_key)
            if data_obj is not None:
                for tag, value in data_obj.items():
                    if self._goodKey(tag):
                        self.mTagSets[tag].add(rec_no)
                        self.mMarkedSet.add(rec_no)
        self.mIntVersion += 1

    def getTagRecordList(self, tag):
        return sorted(self.mTagSets[tag])

    def getTagList(self):
        return sorted(self.mTagSets.keys())

    def getVariants(self):
        return self.getTagList()

    @staticmethod
    def _goodPair(key_value):
        return key_value[0] and key_value[0][0] != '_'

    @staticmethod
    def _goodKey(key):
        return key and key[0] != '_'\

    def makeRecReport(self, rec_no, tags_to_update):
        rec_key = self.getWS().getDataSet().getRecKey(rec_no)
        rec_data = self.getWS().getMongoConn().getRecData(rec_key)
        mark_modified = False
        if tags_to_update is not None:
            rec_data, mark_modified = self._changeRecord(
                rec_no, rec_key, rec_data, tags_to_update)
        ret = {"all-tags": self.getTagList()}
        if mark_modified:
            ret["marker"] = [rec_no, rec_no in self.mMarkedSet]
        if rec_data is None:
            ret["tags"] = dict()
            return ret
        ret["tags"] = dict(filter(self._goodPair, rec_data.items()))
        history = rec_data.get('_h')
        if history is not None:
            idx_h, len_h = history[0], len(history[1])
            if idx_h > 0:
                ret["can_undo"] = True
            if idx_h + 1 < len_h:
                ret["can_redo"] = True
        return ret

    @classmethod
    def _makeObj(cls, rec_key, data):
        new_rec_data = {"_id": rec_key}
        if data is not None:
            for key, value in data.items():
                if cls._goodKey(key):
                    new_rec_data[key] = value
        return new_rec_data

    @classmethod
    def _hasTags(cls, rec_data):
        for key in rec_data.keys():
            if cls._goodKey(key):
                return True
        return False

    def _changeRecord(self, rec_no, rec_key, rec_data, tags_to_update):
        if rec_data and rec_data.get('_h') is not None:
            h_idx, h_stack = rec_data['_h']
            h_stack = h_stack[:]
        else:
            h_idx, h_stack = 0, []
        new_rec_data = None
        if tags_to_update == "UNDO":
            if h_idx > 0:
                if h_idx == len(h_stack):
                    h_stack.append(self._makeObj(rec_key, rec_data))
                h_idx -= 1
                new_rec_data = self._makeObj(rec_key, h_stack[h_idx])
                new_rec_data['_h'] = [h_idx, h_stack]
        elif tags_to_update == "REDO":
            if rec_data and rec_data.get('_h') is not None:
                h_idx, h_stack = rec_data['_h']
                if h_idx + 1 < len(h_stack):
                    h_idx += 1
                    new_rec_data = self._makeObj(rec_key, h_stack[h_idx])
                    new_rec_data['_h'] = [h_idx, h_stack]
        else:
            new_rec_data = self._makeObj(rec_key, tags_to_update)
            h_stack = h_stack[:h_idx + 1]
            if rec_data is not None:
                h_stack.append(self._makeObj(rec_key, rec_data))
            if len(h_stack) > 10:
                h_stack = h_stack[-10:]
            new_rec_data['_h'] = [len(h_stack), h_stack]
        if new_rec_data is None:
            return rec_data, False
        self.getWS().getMongoConn().setRecData(
            rec_key, new_rec_data, rec_data)
        tags_prev = set(rec_data.keys() if rec_data is not None else [])
        tags_new  = set(new_rec_data.keys())
        list_modified = False
        for tag_name in tags_prev - tags_new:
            if self._goodKey(tag_name):
                self.mTagSets[tag_name].remove(rec_no)
                list_modified |= not self.mTagSets[tag_name]
        for tag_name in tags_new - tags_prev:
            if self._goodKey(tag_name):
                list_modified |= not self.mTagSets[tag_name]
                self.mTagSets[tag_name].add(rec_no)
        if list_modified:
            self.mIntVersion += 1
        mark_modified = False
        if self._hasTags(new_rec_data):
            if rec_no not in self.mMarkedSet:
                self.mMarkedSet.add(rec_no)
                mark_modified = True
        else:
            if rec_no in self.mMarkedSet:
                self.mMarkedSet.remove(rec_no)
                mark_modified = True
        return new_rec_data, mark_modified

    def restrict(self, rec_no_seq, variants):
        rec_no_set = set(rec_no_seq)
        work_set = set()
        for tag_name in variants:
            tag_set = self.mTagSets.get(tag_name)
            if tag_set:
                work_set |= (tag_set & rec_no_set)

        return sorted(work_set)
