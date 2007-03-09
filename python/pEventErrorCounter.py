

class pEventErrorCounter:

    def __init__(self):
        self.__Counter = {}

    def reset(self):
        self.Counter = {}

    def fill(self, key):
        try:
            self.__Counter[key] += 1
        except KeyError:
            self.__Counter[key] = 1

    def getNumErrors(self, key):
        try:
            return self.__Counter[key]
        except KeyError:
            return 0

    def __str__(self):
        out = 'Event errors counter information:\n'
        for (key, value) in self.__Counter.items():
            out += '%s:\t%d\n' % (key, value)
        return out


if __name__ == '__main__':
    counter = pEventErrorCounter()
    for i in range(10):
        counter.fill('GTRC FIFO full')
    for i in range(3):
        counter.fill('GTCC timeout')
    counter.fill('GTFE phasing error')
    print counter
