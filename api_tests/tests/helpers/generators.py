from time import gmtime, strftime

testDataPrefix = 'Autotest-'


class Generator:
    def unique_name(self):
        return testDataPrefix + str(self) + strftime("-%y-%m-%d_%H-%M-%S", gmtime())
