import codecs, os, json

#========================================
def loadJSonConfig(config_file):
    with codecs.open(config_file, "r", encoding = "utf-8") as inp:
        content = inp.read()
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
