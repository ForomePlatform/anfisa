import argparse
import glob
import json
import os
import subprocess
import tempfile
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Annotate VCF file with VEP and output results as JSON")
    parser.add_argument("-i", "--input", dest = "input", help="VCF")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    parser.add_argument("-c", "--case", dest="case", help="Case name, default is determined from directory name")
    parser.add_argument("-d", "--dir", dest="dir", help="Work directory", default=os.getcwd())
    parser.add_argument("-p", "--platform", dest="platform", help="Platform: wes/wgs/panel")
    parser.add_argument("-r", "--reuse", action='store_true', help="resue intermediate files from previous run")
    parser.add_argument("-n", "--donotrun", action='store_true', help="Generate Inventory and exit")

    args = parser.parse_args()
    print (args)

    working_dir =  args.dir
    case = args.case if args.case else os.path.basename(working_dir).split('_')[0]
    if (args.input):
        input_file = args.input
    else:
        vcfs = glob.glob(os.path.join(working_dir,"*{}*vcf*".format(case)))
        vcfs = [vcf for vcf in vcfs if not vcf.endswith('idx')]
        if len(vcfs) == 0:
            raise Exception("No VCF files are found in {}".format(working_dir))
        elif len(vcfs) > 1:
            raise Exception("Ambiguos VCF files are in {}: {}".format(working_dir, ", ".join(vcfs)))
        else:
            input_file = os.path.basename(vcfs[0])

    x = input_file.lower().split('.')[0].split('_')
    if ('wgs' in x):
        raw_platform = 'wgs'
    elif ('wes' in x):
        raw_platform = 'wes'
    else:
        raw_platform = "unknown"

    if args.platform:
        platform = args.platform
    else:
        platform = raw_platform

    if (platform):
        print ("Platform: {}".format(platform))
    else:
        platform = "wgs"
        print ("Could not determine platform (WES or WGS), assuming: ".format(platform))

    working_dir = args.dir
    case_id = "{}_{}".format(case, platform)
    fam_file = "{}.fam".format(case)

    patient_ids_file = os.path.join(working_dir, "samples-{}.csv".format(case))
    if (not os.path.exists(patient_ids_file)):
        patient_ids_file = None
    else:
        patient_ids_file = "$"

    if (input_file.endswith(".gz")):
        os.system("gunzip {}".format(input_file))
        input_file = input_file[:-3]

    if (args.output):
        output = args.output
    else:
        output = "${NAME}_anfisa.json.gz"

    if (args.reuse):
        vep_json = input_file[0:-4] + ".vep.json"
    else:
        vep_json = None

    config = dict()
    config["aliases"]       = {"CASE":case}
    if (platform in ["wes", "wgs"]):
        config["aliases"]["PLATFORM"] = platform
        config["platform"]  =  "${PLATFORM}"
    else:
        config["platform"]  =  raw_platform
    config["name"]          =  "${NAME}"
    config["config"]        =  "${DIR}/config.json"
    config["fam"]           =  "${DIR}/${CASE}.fam"
    if patient_ids_file == "$":
        config["patient-ids"]   =  "${DIR}/samples-${CASE}.csv"
    elif patient_ids_file:
        config["patient-ids"]   = patient_ids_file
    config["vcf"]           =  "${DIR}/" + input_file.replace(case_id, "${NAME}").replace(case, "${CASE}")
    if (vep_json):
        config["vep-json"]      =  "${DIR}/" + vep_json
    config["anno-log"]      =  "annotations.log"
    config["a-json"]        =  "${DIR}/" + output
    config["docs"]          =  []
    
    inventory = os.path.join(working_dir, "{}.cfg".format(case_id))

    with open(inventory, "w") as cfg:
        json.dump(config, cfg, indent=4)

    print ("Inventory: " + inventory)
    if args.donotrun:
        sys.exit(0)

    temp_dir = tempfile.mkdtemp(dir=working_dir, prefix="tmp_a_")

    executable = "java"
    jar = "/data/projects/Annotations/lib/annotation.jar"
    main = "org.forome.annotation.annotator.main.AnnotatorMainFork"
    annotator_cfg = "/data/projects/Annotations/lib/bgm.json"

    args = ["-cp", jar, main, "-config", annotator_cfg, "-inventory", inventory]

    child_pid = os.fork()
    if (child_pid):
        print ("Starting child process: {} => {}".format(str(os.getpid()), str(child_pid)))
        sys.exit(0)
    else:
        os.chdir(temp_dir)
        pid = os.getpid()
        sys.stdout = open("out-{}.log".format(str(pid)), "w")
        sys.stderr = open("err-{}.log".format(str(pid)), "w")
        # args = ["-version"]
        print ("Executing {} {}".format(executable, " ".join(args)))
        #os.execvp(executable, args)
        subprocess.call([executable] + args, stdout=sys.stdout, stderr=sys.stderr)




