#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from forome_tools.log_err import logException
from .view_repr import jsonHtmlRepr, htmlEscape
#===============================================
class AttrH:
    @classmethod
    def normLink(cls, value):
        return value

    #===============================================
    def __init__(self, name, kind = None, title = None,
            is_seq = False, tooltip = None, render_mode = None,
            requires = None):
        assert kind != "place" or name.lower() == name, (
            f"Placement attribute {name}: must be lowercase")
        self.mAspect = None
        self.mName = name
        self.mTitle = (title if title is not None else name)
        self.mKinds = kind.split() if kind else ["norm"]
        self.mToolTip = tooltip
        self.mIsSeq = is_seq
        self.mRenderMode = render_mode
        self.mReprFunc = None
        self.mRequires = requires

    def setAspect(self, asp):
        self.mAspect = asp

    def reset(self, kind, is_seq):
        self.mKinds = kind.split() if kind else ["norm"]
        self.mIsSeq = is_seq

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def isSeq(self):
        return self.mIsSeq

    def getToolTip(self):
        return self.mToolTip

    def getRenderMode(self):
        return self.mRenderMode

    def hasKind(self, kind):
        return kind in self.mKinds

    def getMainKind(self):
        return self.mKinds[0]

    def getKinds(self):
        return iter(self.mKinds)

    def getFullName(self):
        return self.mAspect.getName() + '.' + self.mName

    def setReprFunc(self, repr_func):
        self.mReprFunc = repr_func

    def getRequirements(self):
        return self.mRequires

    #===============================================
    def dump(self):
        ret = {
            "name": self.mName, "kind": " ".join(self.mKinds),
            "title": self.mTitle, "is_seq": self.mIsSeq}
        if self.mToolTip:
            ret["tooltip"] = self.mToolTip
        if self.mRequires:
            ret["requires"] = sorted(self.mRequires)
        return ret

    @classmethod
    def load(cls, data):
        return cls(data["name"], data["kind"], data["title"],
            is_seq = data["is_seq"], tooltip = data.get("tooltip"),
            requires = data.get("requires"))

    #===============================================
    def htmlRepr(self, obj, view_context):
        val_obj = "-undef-"
        try:
            val_obj = obj.get(self.mName) if obj else None
            if self.mReprFunc:
                return self.mReprFunc(val_obj, view_context)
            repr_text = None
            if val_obj is True:
                return ("True", self.getMainKind())
            if val_obj is False:
                return ("False", self.getMainKind())
            if val_obj == 0 and isinstance(val_obj, int):
                return ("0", self.getMainKind())
            if val_obj == 0 and isinstance(val_obj, float):
                return ("0.0", self.getMainKind())
            if val_obj:
                if self.mIsSeq:
                    seq = []
                    for it_obj in val_obj:
                        it_repr = self._htmlRepr(it_obj)
                        if it_repr:
                            seq.append(it_repr)
                    repr_text = ', '.join(seq)
                else:
                    repr_text = self._htmlRepr(val_obj)
            if repr_text is None:
                return ("-", "none")
            if not repr_text:
                return ("&emsp;", "none")
            return (repr_text, self.getMainKind())
        except Exception:
            logException("Problem with attribute %s: obj = %r" %
                (self.getFullName(), val_obj))
            return ("???", "none")

    def _htmlRepr(self, value):
        if (not value and not isinstance(value, int)
                and not isinstance(value, float)):
            return None
        if "json" in self.mKinds:
            return jsonHtmlRepr(value)
        if not value:
            return None
        if "link" in self.mKinds:
            link = self.normLink(value)
            return ('<span title="%s"><a href="%s" target="%s">'
                'link</a></span>' % (link, link, self.mName))
        return htmlEscape(value)
