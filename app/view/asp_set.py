from .aspect import AspectH

#===============================================
class AspectSetH:
    def __init__(self, aspects):
        self.mAspects = aspects

    def __getitem__(self, name):
        for asp in self.mAspects:
            if asp.getName() == name:
                return asp
        return None

    def __iter__(self):
        return iter(self.mAspects)

    #===============================================
    def dump(self):
        return [asp.dump() for asp in self.mAspects]

    @classmethod
    def load(cls, data):
        return cls([AspectH.load(it) for it in data])

    #===============================================
    def getViewRepr(self, rec_data, research_mode, details = None):
        ret = []
        for aspect in self.mAspects:
            if aspect.isIgnored():
                continue
            if aspect.checkResearchBlock(research_mode):
                continue
            ret.append(aspect.getViewRepr(rec_data, research_mode, details))
        return ret

    def getFirstAspectID(self):
        return self.mAspects[0].getName()

    def setAspectHitGroup(self, aspect_name, group_attr):
        for aspect in self.mAspects:
            if aspect.getName() == aspect_name:
                aspect.getColGroups().setHitGroup(group_attr)
                return
        assert False, "Failed to find aspect for hit group"
