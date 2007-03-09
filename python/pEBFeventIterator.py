
import logging
import LDF

class pEBFeventIterator(LDF.LDBI_EBFeventIterator):

    def __init__(self, latComponentIterator):
        LDF.LDBI_EBFeventIterator.__init__(self, latComponentIterator)
        self.__LatComponentIterator = latComponentIterator

    def handleError(self, event, code, p1, p2):
        fn = 'pEBFeventIterator.handleError()'
        if code == LDF.EBFeventIterator.ERR_NonEBFevent:
            logging.error('%s: non-EBF event contribution.' % fn)
            return 1
        else:
            logging.error('%s: unknown error code.' % fn)
            return 0
    
    def process(self, evt):
        if evt.status() != 0:
            fn = 'pEBFeventIterator.process()'
            logging.error('%s: bad status in event header.')
            return evt.status()
        else:
            self.__LatComponentIterator.iterate(evt)
            return self.__LatComponentIterator.status()
