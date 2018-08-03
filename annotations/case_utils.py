
def parse_fam_file(fam_file):

    samples = dict()

    with open (fam_file) as input:
        for line in input:
            if line.startswith('#') or not line:
                continue
            try:
                family, id, father, mother, sex, affected = line.split()
                sample = dict()
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
