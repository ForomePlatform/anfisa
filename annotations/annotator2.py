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

    args = parser.parse_args()
    print args

    working_dir =  args.dir
    case = args.case if args.case else os.path.basename(working_dir).split('_')[0]
    if (args.input):
        input_file = args.input
    else:
        vcfs = glob.glob(os.path.join(working_dir,"*{}*vcf*".format(case)))
        if len(vcfs) == 0:
            raise Exception("No VCF files are found in {}".format(working_dir))
        elif len(vcfs) > 1:
            raise Exception("Ambiguos VCF files are in {}: {}".format(working_dir, ", ".join(vcfs)))
        else:
            input_file = vcfs[0]

    x = input_file.lower().split('_')
    if args.platform:
        platform = args.platform
    elif ('wgs' in x):
        platform = 'wgs'
    elif ('wes'in x):
        platform = 'wes'
    else:
        platform = "panel"

    if (platform):
        print "Platform: {}".format(platform)
    else:
        platform = "wgs"
        print "Could not determine platform (WES or WGS), assuming: ".format(platform)

    working_dir = args.dir
    case_id = "{}_{}".format(case, platform)
    fam_file = "{}.fam".format(case)

    patient_ids_file = os.path.join(working_dir, "samples-{}.csv".format(case))
    if (not os.path.exists(patient_ids_file)):
        patient_ids_file = None

    if (input_file.endswith(".gz")):
        os.system("gunzip {}".format(input_file))
        input_file = input_file[:-3]

    if (args.output):
        output = args.output
    else:
        output = "${ID}_anfisa.json.gz"

    config = dict()
    config["aliases"]       = {"ID":case_id, "CASE":case}
    config["name"]          =  "${ID}"
    config["platform"]      =  platform
    config["config"]        =  "${DIR}/config.json"
    config["fam"]           =  "${DIR}/${CASE}.fam"
    config["patient-ids"]   =  "${DIR}/samples-${CASE}.csv"
    config["vcf"]           =  "${DIR}/" + input_file
    # config["vep-json"]      =  "${DIR}/${ID}_vep.json"
    config["anno-log"]      =  "${DIR}/annotations-${CASE}.log"
    config["a-json"]        =  "${DIR}/" + output
    config["docs"]          =  []
    
    inventory = os.path.join(working_dir, "{}.cfg".format(case_id))

    with open(inventory, "w") as cfg:
        json.dump(config, cfg, indent=4)

    temp_dir = tempfile.mkdtemp(dir=working_dir, prefix="tmp_a_")

    executable = "java"
    jar = "/home/vulitin/deploy/annotationservice/exec/annotation_v.0.5.0.14.jar"
    main = "org.forome.annotation.annotator.main.AnnotatorMainFork"
    annotator_cfg = "/home/vulitin/deploy/annotationservice/exec/config.json"

    args = ["-cp", jar, main, "-config", annotator_cfg, "-inventory", inventory]

    child_pid = os.fork()
    if (child_pid):
        print "Starting child process: {} => {}".format(str(os.getpid()), str(child_pid))
        sys.exit(0)
    else:
        os.chdir(temp_dir)
        pid = os.getpid()
        sys.stdout = open("out-{}.log".format(str(pid)), "w")
        sys.stderr = open("err-{}.log".format(str(pid)), "w")
        # args = ["-version"]
        print "Executing {} {}".format(executable, " ".join(args))
        #os.execvp(executable, args)
        subprocess.call([executable] + args, stdout=sys.stdout, stderr=sys.stderr)




