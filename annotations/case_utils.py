import glob
import os
import sortedcontainers


def parse_fam_file(fam_file):

    samples = sortedcontainers.SortedDict()

    case_dir, file_name = os.path.split(fam_file)
    case = file_name.split('.')[0]
    map_file = None
    maps = glob.glob(os.path.join(case_dir, "samples*"))
    if len(maps) == 1:
        map_file = maps[0]
    elif len(maps) > 1:
        maps = [m for m in maps if case in m]
        if (len(maps) > 0):
            map_file = maps[0]

    sample_map = dict()
    if (map_file):
        with open (map_file) as input:
            lines = input.readlines()
            for line in lines:
                tokens = line.split()
                internal_names = [t for t in tokens if case in t.strip()]
                external_names = [t for t in tokens if "CP" in t.strip()]
                if (not external_names):
                    external_names = tokens[0:1]
                if (len (internal_names) == 1 and len(external_names) == 1):
                    sample_map[internal_names[0]] = external_names[0]
                elif (len (internal_names) == 0):
                    raise Exception("Line {}: missing mapping for sample: {}*".format(line, case))
                elif (len(external_names) == 0):
                    raise Exception("Line {}: missing mapping for sample: CP*".format(line))
                else:
                    raise Exception("Ambiguous sample mapping: {}".format(line))


    with open (fam_file) as input:
        for line in input:
            if line.startswith('#') or not line:
                continue
            try:
                family, id, father, mother, sex, affected = line.split()
                sample = dict()
                sample["name"]      = sample_map.get(id, id)
                sample['family']    = family
                sample['id']        = id
                sample['father']    = father
                sample['mother']    = mother
                sample['sex']       = int(sex)
                sample['affected']  = (int(affected) == 2)
                samples[id] = sample
            except:
                raise Exception('Could not parse fam file line: {}'
                                .format(line.strip()))

    return samples
