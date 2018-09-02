from pyliftover import LiftOver

class Converter:
    def __init__(self):
        ## lo = LiftOver("/opt/data/misc/hg38ToHg19.over.chain.gz")
        self.lo = LiftOver('hg19', 'hg38')

    def hg38(self, ch, pos):
        ch = str(ch).lower()
        if (ch.isdigit() or ch == 'x' or ch == 'y'):
            ch = "chr{}".format(ch)
        try:
            coord  = self.lo.convert_coordinate(ch, pos - 1)
        except:
            print "WARNING: HG38 conversion at {}:{}".format(ch, pos)
            coord = None
        if (not coord or len(coord) == 0):
            return None
        r = coord[0][1] + 1
        if (len(coord) == 1):
            return r
        return r, coord


if __name__ == '__main__':
    coordinates = [
        (3,164777814),
        (22,51064480),
        (16,2376465),
        (4,55594075)
    ]

    converter = Converter()
    for c in coordinates:
        r = converter.hg38(*c)
        print "{}   {}->{}".format(c[0], c[1], r)