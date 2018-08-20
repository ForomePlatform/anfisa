import sys

from annotations.gnomad import GnomAD
from annotations.record import Variant

class Stat:
    def __init__(self):
        self.count_true = 0
        self.count_false = 0
        self.count_1 = 0
        self.count_2 = 0
        self.count_2_0 = 0
        self.count_diff = 0

    def t(self):
        self.count_true += 1

    def f(self):
        self.count_false += 1

    def one(self):
        self.count_1 += 1

    def two(self):
        self.count_2 += 1

    def two0(self):
        self.count_2_0 += 1

    def diff(self):
        self.count_diff += 1

    def __str__(self):
        s = "In 1 only: {}\nIn 2 only: {}/{}\nIn both: {}\nIn neither: {}\nIn both incosistent: {}".format(
            self.count_1, self.count_2, self.count_2_0, self.count_true, self.count_false, self.count_diff
        )
        return s


def compare_db_to_file(file):
    stat = Stat()
    gnomAD = GnomAD()
    with open(file) as input:
        while(True):
            line = input.readline()
            if (not line):
                break
            v = Variant(line, gnomAD_connection=gnomAD)
            alt_list = v.alt_list()
            x1 = 0
            af2 = v.get_gnomad_af()
            for alt in alt_list:
                af1 = gnomAD.get_af(v.chr_num(), v.lowest_coord(), v.ref(), alt)
                if (af1):
                    x1 += 1

                if (af1 == None and af2 == None):
                    stat.f()
                elif (af1 == af2):
                    stat.t()
                elif (af1):
                    if (af2 == None):
                        stat.one()
                    else:
                        stat.diff()
                else:
                    stat.two()
            if (af2 and (x1 == 0)):
                stat.two0()

    return stat


if __name__ == '__main__':
    file = sys.argv[1]
    print compare_db_to_file(file)
