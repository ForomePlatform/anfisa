from argparse import ArgumentParser

from storage import dropDataSet, loadJSonConfig, createDataSet
import glob
import os


DEFAULT_PATH_PATTERN = "/net/bgm/cases/?_{platform}/analysis/downstream/?_anfisa.json"


def read_vault(path_to_vault, pattern):
    cases = []
    for p in pattern:
        files = glob.glob(os.path.join(path_to_vault, p))
        cases += [os.path.basename(f) for f in files]
    return cases


def find_json(case_name, path_pattern):
    f = path_pattern.format(name=case_name)
    if (os.path.isfile(f)):
        return f
    f = "{}.gz".format(f)
    if (os.path.isfile(f)):
        return f
    #raise Exception("Annotated json not found: {}".format(f))
    return None


def refresh_case(app_config, case_name, path_to_json, mode):
    dropDataSet(app_config, case_name, mode, True)
    createDataSet(app_config, case_name, mode,
        case_name, path_to_json, 500)


if __name__ == '__main__':
    parser = ArgumentParser("Refresh cases in Anfisa")
    parser.add_argument("-c", "--config", default="anfisa.json", help="Configuration file,  default=anfisa.json")
    parser.add_argument("-m", "-k", "--mode", "--kind", help="Mode: ws/xl", default="ws")
    parser.add_argument("names", nargs=1, help="Dataset name pattern")
    parser.add_argument("-w", "--platform", default="wes", help="Sequencing Platform: wes/wgs")
    parser.add_argument("-p", "--path", default=DEFAULT_PATH_PATTERN, help="Pattern to look for annotated json by case name")
    run_args = parser.parse_args()

    path_to_json = run_args.path
    if ("{platform}" in path_to_json):
        platform = run_args.platform
        path_to_json = path_to_json.format(platform=platform)
    path_to_json = path_to_json.replace("?", "{name}")

    app_config = loadJSonConfig(run_args.config)
    mode = run_args.mode

    cases = read_vault(app_config["data-vault"], run_args.names)
    n = 0
    for c in cases:
        p = find_json(c, path_to_json)
        if (not p):
            print "Annotated json not found for: {}, skipping".format(c)
        refresh_case(app_config, c, p, mode)
        n = n + 1
        print "Refreshed: {}, {}/{}".format(c, n, len(cases))

    print "Refreshed {} cases".format(n)

