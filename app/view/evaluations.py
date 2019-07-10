

def get(obj,path):
    x = path.split('/')[1:]
    for key in x:
        obj = obj.get(key)
        if not obj:
            return obj
    return obj

RED = 'red'
GREEN = 'green'
YELLOW = 'yellow'

CIRCLE = ''
CROSS = '-cross'

csq_damaging = [
    'transcript_ablation',
    'splice_acceptor_variant',
    'splice_donor_variant',
    'stop_gained',
    "frameshift_variant",
    'stop_lost',
    'start_lost'
]

csq_missense = [
    "transcript_amplification",
    "inframe_insertion",
    "inframe_deletion",
    "missense_variant",
    "protein_altering_variant"
]

predictions = {
    "polyphen": [{'benign': 0}, {'possibly_damaging': 10}, {'probably_damaging': 10}, {'damaging': 20}],
    "polyphen2_hvar": [{'B': 0}, {'P': 10}, {'D': 20}],
    "polyphen2_hdiv": [{'B': 0}, {'P': 10}, {'D': 20}],
    "sift": [{'tolerated': 0}, {'deleterious': 20}],
    "mutation_taster": [{10: 0}, {'N': 0}, {20: 20}, {'A': 20}],
    "fathmm": [{'T': 0}],
    "mutation_assessor": [{'N': 0}, {'L': 0}, {'M': 10}, {'H': 20}]
}


def get_color_code(obj):
    csq = get(obj, "/data/most_severe_consequence")
    if csq in csq_damaging:
        shape = CROSS
    elif csq in csq_missense:
        shape = CIRCLE
    else:
        shape = CIRCLE

    hgmd_pred = get(obj, "/view/databases/hgmd_tags")
    if (hgmd_pred):
        if 'D' in hgmd_pred or 'DM' in hgmd_pred:
            return RED + shape

    clinvar_benign = get(obj, "/_filters/clinvar_benign")
    clinvar_trusted_benign = get(obj, "/_filters/clinvar_trusted_benign")

    if clinvar_benign or clinvar_trusted_benign:
        if shape == CROSS:
            return YELLOW + CROSS
        else:
            return GREEN + CIRCLE

    clinvar_significance = get(obj, "/data/clinvar_significance")
    if clinvar_significance:
        for s in clinvar_significance:
            ss = s.lower()
            if 'pathogenic' in ss:
                return RED + shape
            if 'conflict' in ss and clinvar_trusted_benign == False:
                return RED + shape

    best = 100
    worst = -1
    
    for p in predictions:
        lov = get(obj, "/view/predictions/{}".format(p))
        for v in lov:
            x = -1
            if not v:
                continue
            tr = predictions[p]
            for element in tr:
                x = element.get(v)
                if x:
                    break
            if x < 0:
                continue

            if x < best:
                best = x
            if x > worst:
                worst = x

    color = None
    if (0 < best and 20  <= worst):
        color = RED
    elif (0 == best and worst <= 0):
        color = GREEN
    elif (best < 100 or worst > -1):
        color = YELLOW


    if color:
        return color + shape

    if shape == CROSS:
        return YELLOW + shape

    return None

