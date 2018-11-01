import numbers

#===============================================
class Types:
    sTypes = [None, "null", "list", "dict", "empty", "link", "string",
        "int", "numeric"]
    # and "undef", "json"

    @staticmethod
    def _detectValTypes(value):
        if value is None:
            return [1]
        elif isinstance(value, list):
            return [2]
        elif isinstance(value, dict):
            return [3]
        elif isinstance(value, basestring):
            if not value:
                return [4, 5, 6]
            elif value.startswith("http"):
                if value.startswith("https:") or value.startswith("http:"):
                    return [5, 6]
            return [6]
        elif isinstance(value, int):
            return [7, 8]
        elif isinstance(value, numbers.Number):
            return [8]
        return None

    @classmethod
    def detectValTypes(cls, value):
        kind_idxs = cls._detectValTypes(value)
        ret = set()
        if kind_idxs:
            for idx in kind_idxs:
                if cls.sTypes[idx]:
                    ret.add(cls.sTypes[idx])
        return ret

    @classmethod
    def filterTypeKind(cls, kinds):
        for kind in kinds:
            if kind in cls.sTypes:
                return kind
        return None
