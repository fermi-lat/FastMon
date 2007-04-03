## @package pLATcomponentIterator
## @brief Package responsible for the whole event iteration stuff.

import logging
import LDF

from pTKRcontributionIterator     import pTKRcontributionIterator
from pCALcontributionIterator     import pCALcontributionIterator
from pAEMcontributionIterator     import pAEMcontributionIterator
from pERRcontributionIteratorBase import pERRcontributionIteratorBase
from pGEMcontribution             import pGEMcontribution


## @brief Implementation of the LAT component iterator.

class pLATcomponentIterator(LDF.LATcomponentIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for the creation and filling
    #  of the output ROOT tree.
    ## @param errorCounter
    #  The pEventErrorCounter responsible for keeping track of the errors.
  
    def __init__(self, treeMaker, errorCounter):

        ## @var __TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  and filling of the output ROOT tree.

        ## @var __ErrorCounter
        ## @brief The pEventErrorCounter responsible for keeping track of
        #  the errors.
        
        LDF.LATcomponentIterator.__init__(self)
        self.__TreeMaker    = treeMaker
        self.__ErrorCounter = errorCounter

    ## @brief Implementation of the GEM component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.

    def GEMcomponent(self, event, contribution):
        gemContribution = pGEMcontribution(event, contribution,\
                                           self.__TreeMaker)
        gemContribution.fillEventContribution()
        return 0 

    ## @brief Implementation of the TKR component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
        
    def TKRcomponent(self, event, contribution):
        tkrIterator = pTKRcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        tkrIterator.iterate()
        tkrIterator.fillEventContribution()
        if tkrIterator.diagnostic() is not None:
            self.TKRend(tkrIterator.diagnostic())
        return 0

    ## @brief Implementation of the CAL component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
    
    def CALcomponent(self, event, contribution):
        calIterator = pCALcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        calIterator.iterate()
        calIterator.fillEventContribution()
        self.CALend(calIterator.CALend())
        return 0

    ## @brief Implementation of the ACD component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.

    def ACDcomponent(self, event, contribution):
        aemIterator = pAEMcontributionIterator(event, contribution,\
                                               self.__TreeMaker)
        aemIterator.iterate()        
	aemIterator.fillEventContribution()
        return 0

    ## @brief Implementation of the error component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.

    def error(self, event, contribution):
        if not LDF.EventSummary.error(contribution.summary()):
            return
        if self.diagnosticEnd() != 0:
            offset = self.diagnosticEnd()
        else:
            offset = TKRend()
        errIterator = pERRcontributionIteratorBase(event, contribution,\
                                                   offset, self.__ErrorCounter)
	errIterator.iterate()
        return 0

    ## @brief Handle packet errors.
    ## @param self
    #  The class instance.
    ## @param contribution
    #  The contribution object.
    ## @param code
    #  The error code.
    ## @param p1
    #  Parameter 1.
    ## @param p2
    #  Parameter 2.
    
    def handleError(self, contribution, code, p1, p2):
        if type(contribution) == LDF.EBFevent:
            if code == LDF.EBFcontributionIterator.ERR_PacketError:
                self.__ErrorCounter.fill('PACKET_ERROR')
            return 0
