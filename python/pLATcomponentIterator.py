## @package pLATcomponentIterator
## @brief Package responsible for the whole event iteration stuff.

import LDF
from pGlobals  import *

from pTKRcontributionIterator     import pTKRcontributionIterator
from pCALcontributionIterator     import pCALcontributionIterator
from pAEMcontributionIterator     import pAEMcontributionIterator
from pERRcontributionIteratorBase import pERRcontributionIteratorBase
from pGEMcontribution             import pGEMcontribution

import pSafeLogger
logger = pSafeLogger.getLogger('pLATcomponentIterator')


## @brief Implementation of the LAT component iterator.

class pLATcomponentIterator(LDF.LATcomponentIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for the creation and filling
    #  of the output ROOT tree.
    ## @param errorHandler
    #  The pErrorHandler responsible for keeping track of the errors.
  
    def __init__(self, treeMaker, errorHandler):

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  and filling of the output ROOT tree.

        ## @var ErrorHandler
        ## @brief The pErrorHandler responsible for keeping track of
        #  the errors.
        
        LDF.LATcomponentIterator.__init__(self)
        self.TreeMaker    = treeMaker
        self.ErrorHandler = errorHandler

    ## @brief Implementation of the GEM component.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.

    def GEMcomponent(self, event, contribution):
        gemContribution = pGEMcontribution(event, contribution,\
                                           self.TreeMaker     ,\
                                           self.ErrorHandler)
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
                                               self.TreeMaker     ,\
                                               self.ErrorHandler)
	rc     = tkrIterator.iterate()
	status = tkrIterator.status()
	# Note Trying to fill the event contribution only if the event has no error
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
                                               self.TreeMaker     ,\
                                               self.ErrorHandler)
        rc     = calIterator.iterate() 
        status = calIterator.status() 
	# Note Trying to fill the event contribution only if the event has no error
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
                                               self.TreeMaker     ,\
                                               self.ErrorHandler)
        rc     = aemIterator.iterate()        
        status = aemIterator.status()        
	# Note Trying to fill the event contribution only if the event has no error
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
                                                   offset, self.ErrorHandler)
	errIterator.iterate()
        return 0


    ## @brief Handle packet errors.
    #  From Ric Claus and C++ code
    #  
    #  The LookupErrorCode function is in Common/python/pGlobals
    #
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
    ## Error types 
    #  ERR_NumContributions : Number of contributions found too big
    #  ERR_PastEnd          : Iterated past end of event
    #  ERR_ZeroLength       : Found a contribution with zero length
    #  ERR_PacketError      : Packet Error (Parity, Truncated, WriteFault, TimedOut)
    #  ERR_NoMap            : No contribution map exists for EBF version
    #  ERR_SeqNoMismatch    : Event has nonmatching sequence numbers
    #  ERR_TrgParityError   : Contribution with ID has a Trigger Parity Error
    #
    
    def handleError(self, contribution, code, p1, p2):
        DICT = {LDF.EBFcontribution.Parity     : 'parity'     ,\
                LDF.EBFcontribution.Truncated  : 'truncated'  ,\
                LDF.EBFcontribution.WriteFault : 'write fault',\
                LDF.EBFcontribution.TimedOut   : 'timed out'  ,\
                }
        if type(contribution) == LDF.EBFevent:
            s = LDF.EBFcontributionIterator.handleError(self, contribution, code, p1,p2)
            errName = LookupErrorCode(self, code)[4:]
            if errName == 'PacketError':
		try:
		    errtype = DICT[p1]
		except:
		    errtype = 'unknown'
                self.ErrorHandler.fill('PACKET_ERROR', [errtype])
            else:
               self.ErrorHandler.fill('EBF_CONTRIB_ERROR', [errName, p1, p2])
            return s
	# If the contribution is not EBF then we just return the error code
	return code

