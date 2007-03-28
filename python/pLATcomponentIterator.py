
import logging
import LDF

from pTKRcontributionIterator     import pTKRcontributionIterator
from pCALcontributionIterator     import pCALcontributionIterator
from pAEMcontributionIterator     import pAEMcontributionIterator
from pERRcontributionIteratorBase import pERRcontributionIteratorBase
from pGEMcontribution             import pGEMcontribution

class pLATcomponentIterator(LDF.LATcomponentIterator):
  
    def __init__(self, treeMaker, errorCounter):
        LDF.LATcomponentIterator.__init__(self)
        self.__TreeMaker    = treeMaker
        self.__ErrorCounter = errorCounter

    def GEMcomponent(self, event, contribution):
        gemContribution = pGEMcontribution(event, contribution,\
                                           self.__TreeMaker)
        gemContribution.fillEventContribution()
        return 0 
        
    def TKRcomponent(self, event, contribution):
        tkrIterator = pTKRcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        tkrIterator.iterate()
        tkrIterator.fillEventContribution()
        if tkrIterator.diagnostic() is not None:
            self.TKRend(tkrIterator.diagnostic())
        return 0
    
    def CALcomponent(self, event, contribution):
        calIterator = pCALcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        calIterator.iterate()
        calIterator.fillEventContribution()
        self.CALend(calIterator.CALend())
        return 0

    def ACDcomponent(self, event, contribution):
        aemIterator = pAEMcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        aemIterator.iterate()        
	aemIterator.fillEventContribution()
        return 0

    def error(self, event, contribution):
        if not LDF.EventSummary.error(contribution.summary()):
            return
        if self.diagnosticEnd() != 0:
            offset = self.diagnosticEnd()
        else:
            offset = TKRend()
        errIterator = pERRcontributionIteratorBase(event, contribution,\
                                                   offset, self.ErrorCounter)
        return 0
    
    def handleError(self, contribution, code, p1, p2):
        if type(contribution) == LDF.EBFevent:
            if code == LDF.EBFcontributionIterator.ERR_PacketError:
                pass
            return 0
