
import logging
import LDF


class pERRcontributionIteratorBase(LDF.ERRcontributionIterator):
    
    def __init__(self, event, contribution, offset, lat):
        LDF.ERRcontributionIterator.__init__(self, event, contribution)
        self.offset(offset)
        self.Node = lat
    
    def fillEventContribution(self):
        pass

    def gcccError(self, tower, gccc, err):
        return 0

    def gtccError(self, tower, gtcc, err):
        return 0

    def phaseError(self, tower, err):
        return 0

    def timeoutError(self, tower, err):
        return 0

    def gtrcPhaseError(self, tower, gtcc, gtrc, err):
        return 0

    def gtfePhaseError(self, tower, gtcc, gtrc, err1, err2, err3, err4, err5):
        return 0

    def gtccFIFOerror(self, tower, gtcc, err):        
        return 0

    def gtccTMOerror(self, tower, gtcc):
        return 0

    def gtccHDRParityError(self, tower, gtcc):
        return 0

    def gtccWCParityError(self, tower, gtcc):
        return 0

    def gtrcSummaryError(self, tower, gtcc):
        return 0

    def gtccDataParityError(self, tower, gtcc):
        return 0
