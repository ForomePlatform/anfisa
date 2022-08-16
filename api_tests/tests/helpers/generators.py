from time import gmtime, strftime

testDataPrefix = 'Autotest-'


class Generator:
    @staticmethod
    def unique_name(instanceType):
        return testDataPrefix + instanceType + strftime("-%y-%m-%d_%H-%M-%S", gmtime())
