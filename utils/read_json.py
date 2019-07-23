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
    def __init__(self, source, parse_json = True):
        self.mSources = sorted(glob(source)) if "*" in source else [source]
        self.mCurReader = None
        self.mParseMode = parse_json

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

    def close(self):
        if self.mCurReader is not None:
            self.mCurReader.close()

    def next(self):
        while True:
            if self.mCurReader is not None:
                line = self.mCurReader.next()
                if not line:
                    self.mCurReader.close()
                    self.mCurReader = None
                    continue
                if self.mParseMode:
                    return json.loads(line)
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
def readJSonRecords(src):
    if '*' in src:
        names = sorted(glob(src))
    else:
        names = [src]
    for nm in names:
        if nm.endswith('.gz'):
            with gzip.open(nm, 'rb') as inp:
                for line in inp:
                    yield json.loads(line.decode('utf-8'))
        elif nm.endswith('.bz2'):
            with bz2.BZ2File(nm, 'rb') as inp:
                for line in inp:
                    yield json.loads(line.decode('utf-8'))
        else:
            with open(nm, 'r', encoding = 'utf-8') as inp:
                for line in inp:
                    yield json.loads(line)

