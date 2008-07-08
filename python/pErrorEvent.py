

class pErrorEvent:

    def __init__(self, eventNumber):
        self.EventNumber = eventNumber
        self.ErrorsList  = []

    def addError(self, error):
        self.ErrorsList.append(error)

    def getAsText(self):
        txt = 'Event %s contains error(s):\n' % self.EventNumber
        for error in self.ErrorsList:
            txt += '- %s\n' % error.getAsText()
        return txt

    def getErrorsDict(self):
        dict = {}
        for error in self.ErrorsList:
            dict[error.ErrorCode] = error.getDetailsAsText()
        return dict

    def __str__(self):
        return self.getAsText()


if __name__ == '__main__':
    from pError import pError
    badEvent = pErrorEvent(313)
    badEvent.addError(pError('TEST'))
    badEvent.addError(pError('TEST', [1, 2, 3]))
    print badEvent
       
