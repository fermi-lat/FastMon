## @package pLATcomponentIterator
## @brief Package responsible for the whole event iteration stuff.

import LDF

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
    	    if code == LDF.EBFcontributionIterator.ERR_NumContributions:
    	    	logger.debug("handleError:ERR_NumContributions\n" \
    	    		     "\tNumber of contributions found > %d\n" % p1)
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['Number of Contributions', p1])

    	    elif code == LDF.EBFcontributionIterator.ERR_PastEnd:
    	    	logger.debug("handleError:ERR_PastEnd\n" \
    	    		     "\tIterated past end of event by 0x%0x = %d bytes\n" \
    	    		     % (p1, p1))
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['Past End', p1])

    	    elif code == LDF.EBFcontributionIterator.ERR_ZeroLength:
    	    	logger.debug("handleError:ERR_ZeroLength\n" \
    	    		     "\tFound a contribution with zero length\n")
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['Zero Length'])

            elif code == LDF.EBFcontributionIterator.ERR_PacketError:
	        DICT = {LDF.EBFcontribution.Parity     : 'parity'     ,\
		        LDF.EBFcontribution.Truncated  : 'truncated'  ,\
		        LDF.EBFcontribution.WriteFault : 'write fault',\
		        LDF.EBFcontribution.TimedOut   : 'timed out'  ,\
			}
		try:
		    errtype = DICT[p1]
		except:
		    errtype = 'unknown'
		logger.debug("handleError:ERR_PacketError\n"\
                	     "\tError Type : %s\n" % errtype)
	        self.ErrorHandler.fill('PACKET_ERROR', [errtype])

    	    elif code == LDF.EBFcontributionIterator.ERR_NoMap:
    	    	logger.debug("handleError:ERR_NoMap\n" \
    	    		     "\tNo contribution map exists for EBF version %0x\n"% p1)
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['No Map', p1])

    	    elif code == LDF.EBFcontributionIterator.ERR_SeqNoMismatch:
    	    	logger.debug("handleError:ERR_SeqNoMismatch\n" \
    	    		     "\tEvent has nonmatching sequence numbers %u and %u\n" \
    	    		     % (p1, p2))
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['Sequence Number Mismatch', p1])

    	    elif code == LDF.EBFcontributionIterator.ERR_TrgParityError:
    	    	logger.debug("handleError:ERR_TrgParityError\n" \
    	    		     "\tContribution with ID has a Trigger Parity Error\n")
	    	self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['Trigger Parity Error', p1])

    	    else:
    	        logger.debug("UNKNOWN_ERROR\n"\
              	 	     "\tUnrecognized error code %d = 0x%08x with\n"\
              		     "\targuments %d = 0x%08x, %d = 0x%08x\n"%\
           		     (code, code, p1, p1, p2, p2))
                self.ErrorHandler.fill('EBF_CONTRIB_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])

        return code
