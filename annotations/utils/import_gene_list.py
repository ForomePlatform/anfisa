import os
import sys


def import_gene_list(file, rule_name, target_dir):
    if (not os.path.exists(target_dir)):
        os.mkdir(target_dir)

    with open(file) as input:
        genes = input.readlines()

    with open(os.path.join(target_dir, rule_name + ".py"),"w") as output:
        header = "def evalRec(env, rec):\n" + \
            '    """{}"""\n'.format(rule_name) + \
            "    return (len(set(rec.Genes) &\n" + \
            "        {\n"
        output.write(header)
        for gene in genes:
            output.write("            '{}',\n".format(gene.strip()))

        output.write("        }\n    ) > 0)")

if __name__ == '__main__':
    import_gene_list(*sys.argv[1:])