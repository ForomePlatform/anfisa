import gzip, bz2, json
from glob import glob

#===============================================
class PlainFileReader:
    def __init__(self, fname):
        self.mInput = open(fname, 'r', encoding = 'utf-8')

    def next(self):
        return self.mInput.readline()

    def close(self):
        self.mInput.close()

#===============================================
class GzipFileReader:
    def __init__(self, fname):
        self.mInput = gzip.open(fname, 'rb')

    def next(self):
        return self.mInput.readline().decode('utf-8')

    def close(self):
        self.mInput.close()

#===============================================
class Bz2FileReader:
    def __init__(self, fname):
        self.mInput = bz2.BZ2File.open(fname, 'rb')

    def next(self):
        return self.mInput.readline().decode('utf-8')

    def close(self):
        self.mInput.close()

#===============================================
class JsonLineReader:
    def __init__(self, source, parse_json = True,  transform_f = None):
        self.mSources = sorted(glob(source)) if "*" in source else [source]
        self.mCurReader = None
        self.mParseMode = parse_json
        self.mTransF = transform_f
        self.mCurLineNo = -1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

    def __iter__(self):
        while True:
            line = self.next()
            if line is None:
                break
            yield line

    def getCurLineNo(self):
        return self.mCurLineNo

    def close(self):
        self.mCurLineNo = -1
        if self.mCurReader is not None:
            self.mCurReader.close()

    def next(self):
        return self.readOne()

    def readOne(self):
        while True:
            if self.mCurReader is not None:
                line = self.mCurReader.next()
                self.mCurLineNo += 1
                if not line:
                    self.mCurReader.close()
                    self.mCurReader = None
                    continue
                if self.mParseMode:
                    rec = json.loads(line)
                    if self.mTransF:
                        rec = self.mTransF(rec)
                    return rec
                return line.rstrip()
            if len(self.mSources) == 0:
                return None
            src = self.mSources.pop(0)
            if src.endswith('.gz'):
                self.mCurReader = GzipFileReader(src)
            elif src.endswith('.bz2'):
                self.mCurReader = Bz2FileReader(src)
            else:
                self.mCurReader = PlainFileReader(src)

#===============================================
def readJSonRecords(src,  transform_f = None):
    if '*' in src:
        names = sorted(glob(src))
    else:
        names = [src]
    if transform_f is None:
        process_f = json.loads
    else:
        process_f = lambda line: transform_f(json.loads(line))
    for nm in names:
        if nm.endswith('.gz'):
            with gzip.open(nm, 'rb') as inp:
                for line in inp:
                    yield process_f(line.decode('utf-8'))
        elif nm.endswith('.bz2'):
            with bz2.BZ2File(nm, 'rb') as inp:
                for line in inp:
                    yield process_f(line.decode('utf-8'))
        else:
            with open(nm, 'r', encoding = 'utf-8') as inp:
                for line in inp:
                    yield process_f(line)
