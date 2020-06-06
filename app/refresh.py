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

from argparse import ArgumentParser

from storage import dropDataSet, loadJSonConfig, createDataSet
import glob
import os


DEFAULT_PATH_PATTERN = (
    "/net/bgm/cases/?_{platform}/analysis/downstream/?_anfisa.json")


def read_vault(path_to_vault, pattern):
    cases = []
    for p in pattern:
        files = glob.glob(os.path.join(path_to_vault, p))
        cases += [os.path.basename(f) for f in files]
    return cases


def find_json(case_name, path_pattern):
    fname = path_pattern.format(name = case_name)
    if (os.path.isfile(fname)):
        return fname
    fname = "%s.gz" % fname
    if (os.path.isfile(fname)):
        return fname
    #raise Exception("Annotated json not found: {}".format(f))
    return None


def refresh_case(app_config, case_name, path_to_json, mode):
    dropDataSet(app_config, case_name, mode, True)
    createDataSet(app_config, case_name, mode,
        case_name, path_to_json, 500)


if __name__ == '__main__':
    parser = ArgumentParser("Refresh cases in Anfisa")
    parser.add_argument("-c", "--config", default = "anfisa.json",
        help = "Configuration file,  default=anfisa.json")
    parser.add_argument("-m", "-k", "--mode", "--kind",
        help = "Mode: ws/xl", default="ws")
    parser.add_argument("names", nargs = 1,
        help = "Dataset name pattern")
    parser.add_argument("-w", "--platform", default = "wes",
        help = "Sequencing Platform: wes/wgs")
    parser.add_argument("-p", "--path", default = DEFAULT_PATH_PATTERN,
        help = "Pattern to look for annotated json by case name")
    run_args = parser.parse_args()

    path_to_json = run_args.path
    if ("{platform}" in path_to_json):
        platform = run_args.platform
        path_to_json = path_to_json.format(platform=platform)
    path_to_json = path_to_json.replace("?", "{name}")

    app_config = loadJSonConfig(run_args.config,
        home_path = os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))

    mode = run_args.mode

    vault = app_config["data-vault"]
    cases = read_vault(vault, run_args.names)
    cnt = 0
    for case in cases:
        pf = find_json(case, path_to_json)
        if (not pf):
            print("Annotated json not found for:", case, "skipping")
            continue
        refresh_case(app_config, case, pf, mode)
        #os.chmod(os.path.join(vault,c), 777)
        cnt += 1
        print("Refreshed:", case, "%d/%d" % (cnt, len(cases)))

    print("Refreshed", cnt, "cases")
