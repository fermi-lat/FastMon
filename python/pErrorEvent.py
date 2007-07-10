

class pErrorEvent:

    def __init__(self, eventNumber):
        self.EventNumber = eventNumber
        self.ErrorsList  = []

    def addError(self, error):
        self.ErrorsList.append(error)
    


if __name__ == '__main__':
    from pError import pError
    badEvent = pErrorEvent(313)
    badEvent.addError(pError(313, 'UNPHYSICAL_STRIP_ID', [12, 34, 1753]))
    badEvent.addError(pError(313, 'UNPHYSICAL_STRIP_ID', [12, 34, 1754]))
    print 'Bad event: %d' % badEvent.EventNumber
    for error in badEvent.ErrorsList:
        print '%s (%s)' % (error.ErrorCode, error.getDetails())
       
