import sys, os, json, re

#========================================
sCommentLinePatt = re.compile("^\s*//.*$")

def readCommentedJSon(fname):
    lines = []
    with open(fname, "r", encoding = "utf-8") as inp:
        for line in inp:
            if not sCommentLinePatt.match(line):
                lines.append(line)
    return "".join(lines)

#========================================
def loadJSonConfig(config_file):
    content = readCommentedJSon(config_file)
    dir_name = os.path.abspath(__file__)
    for idx in range(2):
        dir_name = os.path.dirname(dir_name)
    content = content.replace('${HOME}', dir_name)
    pre_config = json.loads(content)

    file_path_def = pre_config.get("file-path-def")
    if file_path_def:
        for key, value in file_path_def.items():
            assert key != "HOME"
            content = content.replace('${%s}' % key, value)
    return json.loads(content)

#========================================
sCommentLinePatt = re.compile("^\s*//.*$")

def loadDatasetInventory(inv_file):
    global sCommentLinePatt

    # Check file path correctness
    dir_path = os.path.dirname(inv_file)
    dir_name = os.path.basename(os.path.dirname(inv_file))
    base_name, _, ext = os.path.basename(inv_file).partition('.')
    if dir_name != base_name or ext != "cfg":
        print("Warning: Improper dataset inventory path:",
            inv_file, file = sys.stderr)

    content = readCommentedJSon(inv_file)
    content = content.replace('${NAME}', base_name)
    content = content.replace('${DIR}', dir_path)
    pre_config = json.loads(content)

    # Replace predefined names
    prenames = pre_config.get("prenames")
    if prenames:
        for key, value in prenames.items():
            assert key != "NAME"
            content = content.replace('${%s}' % key, value)

    # Ready to go
    return json.loads(content)

