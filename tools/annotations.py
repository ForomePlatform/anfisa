import os.path
import sys
from typing import List, Dict, Any
# import yaml
from ruamel.yaml import YAML, yaml_object

from app.config.flt_schema import defineFilterSchema
from app.config.solutions import setupSolutions
from app.config.variables import anfisaVariables
from app.prepare.prep_filters import ViewGroupH
from app.prepare.prep_unit import ValueConvertor, EnumConvertor
from forome_tools.json_conf import loadJSonConfig


yaml = YAML()
yaml.indent(mapping=4, sequence=4, offset=2)
yaml.width = 78


@yaml_object(yaml)
class Annotation:
    yaml_tag = "annotation"
    attributes = set()
    annotations = dict()
    attributes.add("type")
    app_config = None

    type_map = {
        "enum": "categorical",
        "func": "runtime function"
    }

    @classmethod
    def get_dictionary_file(cls):
        my_path = os.path.abspath(__file__)
        root = os.path.dirname(os.path.dirname(my_path))
        dictionary_dir = os.path.join(root, "app", "config", "dictionary")
        if not os.path.isdir(dictionary_dir):
            os.mkdir(dictionary_dir)
        return os.path.join(dictionary_dir, "annotations.yml")

    @classmethod
    def init(cls, path_to_config: str, reset = False):
        cls.app_config = loadJSonConfig(path_to_config)
        if not reset:
            path_to_dictionary = cls.get_dictionary_file()
            if os.path.isfile(path_to_dictionary):
                with open(path_to_dictionary) as f:
                    annotations = yaml.load(f)
                if annotations:
                    for a in annotations:
                        annotation = Annotation(info = None, content=annotations[a])
                        cls.annotations[annotation.name] = annotation
        for var in anfisaVariables.mVariables:
            cls.add_annotation(anfisaVariables.mVariables[var])
        cls.load_filter_set()

    @classmethod
    def update_dictionary(cls):
        path_to_dictionary = cls.get_dictionary_file()
        with open(path_to_dictionary, "wt") as f:
            #yaml.safe_dump(data=cls.annotations, stream=f, indent=4, width=78, default_style=None, line_break='')
            #y.default_style = "|-"
            yaml.dump(data=cls.annotations, stream=f)

    @classmethod
    def map_type(cls, t: str) -> str:
        if t in cls.type_map:
            return cls.type_map[t]
        return t

    @classmethod
    def add_annotation(cls, info: List):
        a = Annotation(info)
        if not a.is_annotation:
            return 
        if a.name in cls.annotations:
            a.merge(cls.annotations[a.name])
        cls.annotations[a.name] = a

    facet_reverse_map = [
        {
            anfisaVariables.mFacetClassifier.mFacetMaps[i][x]: x
            for x in anfisaVariables.mFacetClassifier.mFacetMaps[i]
        }
        for i in range(3)
    ]

    def __init__(self, info: List, content: Dict = None):
        if content is not None:
            self.content = content
            self.is_annotation = True
        else:
            if len(info) != 2:
                raise ValueError()
            self.content = dict()
            self.content["variable_type"] = self.map_type(info[0])
            self.name = None
            self.is_annotation = True
            for attr in info[1]:
                self.add_attribute(attr, info[1][attr])
        self.name = self.content["name"]

    def add_attribute(self, attr: str, value: Any):
        if attr == "classes":
            self.map_classes(value)
            return
        if attr == "render-mode":
            value = self.handle_render_mode(value)
        self.attributes.add(attr)
        if attr in self.content:
            raise ValueError("Duplicate attribute: " + attr)
        self.content[attr] = value

    @staticmethod
    def handle_render_mode(value: str) -> Dict:
        if ',' in value:
            tokens = value.split(',')
            scale = tokens[0]
            bound = tokens[1]
            if bound == '>':
                bstr = "the upper bound"
            elif bound == '<':
                bstr = "the lower bound"
            elif bound == '=':
                bstr = "both upper and lower bounds"
            else:
                raise ValueError(value)
            if scale == "log":
                scale = "logarithmic"
            desc = f"Should be rendered as a {scale} scale. Most often, users select {bstr}."
        elif value in ["bar", "pie"]:
            desc = f"Should be rendered as a {value} chart."
        else:
            desc = f"Should be rendered as a {value}."
        return {
            "id": value,
            "description": desc
        }

    def merge(self, another):
        self.content.update(another.content)
        attr = "used_in_groups"
        if attr in self.content:
            vg = set(self.content[attr])
            self.content[attr] = list(sorted(vg))

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_dict(node.content)
        
    def map_classes(self, classes: List[int]):
        c0 = classes[0]
        fid = self.facet_reverse_map[0][c0]
        if fid == "rules":
            self.is_annotation = False
            return
        if fid == "call":
            self.add_attribute("purpose", "provenance")
        elif fid == "phenotype":
            self.add_attribute("purpose", "phenotype")
        else:
            self.add_attribute("purpose", "evidence")
        for ic in range(len(classes)):
            d = anfisaVariables.mFacetClassifier.getDescr()[ic]
            attr = d["title"]
            values = d["values"]
            fm = self.facet_reverse_map[ic]
            c = classes[ic]
            var_name = values[c]
            value = {
                "id": fm[c],
                "name": var_name
            }
            self.add_attribute(attr, value)

    @classmethod
    def load_filter_set(cls):
        setupSolutions(cls.app_config)
        metadata = {
            "versions": {
                "reference": "hg38"
            }
        }
        filter_set = defineFilterSchema(metadata, "ws")
        for unit in filter_set.mUnits:
            u: ValueConvertor = unit
            aname = u.getName()
            if aname not in cls.annotations:
                continue
            annotation = cls.annotations[aname]

            attr = "used_in_groups"
            content = annotation.content
            if attr not in content:
                content[attr] = []
            vgroup: ViewGroupH = u.mVGroup
            t = vgroup.getTitle()
            if t not in content[attr]:
                content[attr].append(t)

            metadata = u.dump()
            attr = "render-mode"
            if attr not in content and content["variable_type"] == "categorical":
                value = cls.default_render_mode(metadata.get("sub-kind"), metadata.get("mean"))
                content[attr] = cls.handle_render_mode(value)

            attr = "variable_subtype"
            if attr not in content and "sub-kind" in metadata:
                content[attr] = cls.map_subtype(metadata["sub-kind"])
        return

    @staticmethod
    def map_subtype(value: str):
        mapping = {
            "status": "Single categorical value",
            "multi": "Multiple categorical values",
            "transcript-status": "Single categorical value specific to a transcript rather than to a variant",
            "transcript-multiset": "Multiple categorical values where the combination of values is specific to a transcript rather than to a variant",
            "transcript-panels": "A list of selected transcripts (transcript panel)",
            "int": "int",
            "float": "float",
            "transcript-int": "An integer value specific to a transcript rather than to a variant"
        }
        if value not in mapping:
            raise ValueError("Subtype: " + value)
        return {
            "id": value,
            "name": mapping[value]
        }

    @staticmethod
    def default_render_mode(sub_kind, mean):
        if mean == "variety":
            return "tree-map"
        elif sub_kind in {"status", "transcript-status"}:
            return "pie"
        else:
            return "bar"

    def __str__(self):
        return "Annotation: " + self.name


if __name__ == '__main__':
    Annotation.init(sys.argv[1], reset=False)
    Annotation.update_dictionary()
        