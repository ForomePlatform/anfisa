import difflib


def shrink(ref, alt):
    matcher = difflib.SequenceMatcher(a=ref, b=alt)
    matches = matcher.get_matching_blocks()
    a = []
    b = []
    apos = 0
    bpos = 0
    for match in matches:
        a.append(ref[apos:match.a])
        apos = match.a + match.size
        b.append(alt[bpos:match.b])
        bpos = match.b + match.size

    new_ref = ''.join(a)
    new_alt = ''.join(b)
    return new_ref, new_alt


def transform_ref_alt(ref, alt):
    new_ref, new_alt = shrink(ref, alt)
    if (not new_ref or not new_alt):
        first_match = ref[0]
        new_ref = first_match + new_ref
        new_alt = first_match + new_alt

    return new_ref, new_alt


def diff(ref, alt):
    ref1, alt1 = shrink(ref, alt)
    if (not ref1 and not alt1):
        return ""
    else:
        return "{}~{}".format(ref1, alt1)


def cmp_ref_alt(ref1, alt1, ref2, alt2):
    return diff(ref1, alt1) == diff(ref2, alt2)


if __name__ == '__main__':
    print diff("BA", "A")
    print diff("BA", "BA")
    print diff("BACC", "ABCA")
    print diff("BBBBA", "BBBAA")