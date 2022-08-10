from time import gmtime, strftime

testDataPrefix = 'Autotest-'

class Generator:
    def uniqueName(type):
        return testDataPrefix + str(type) + strftime("-%y-%m-%d_%H-%M-%S", gmtime())
