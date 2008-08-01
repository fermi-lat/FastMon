## @package pAEMcontributionIteratorBase
## @brief Package defining the functions for iterating over the ACD
#  event contribution.

import pSafeLogger
logger = pSafeLogger.getLogger('pACDcontributionIteratorBase')

import LDF

from copy import copy

## @brief Base Class for the ACD contribution iterator

class pAEMcontributionIteratorBase(LDF.AEMcontributionIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param contribution
    #  The contribution object.
    ## @param treeMaker
    #  The pRootTreeMaker object responsible for the creation of the ROOT tree.
    ## @param errorHandler
    #  The pErrorHandler object responsible for managing the errors.
    
    def __init__(self, event, contribution, treeMaker, errorHandler):

        ## @var TreeMaker
        ## @brief The pRootTreeMaker object responsible for the creation
        #  of the ROOT tree.

        ## @var ErrorHandler
        ## @brief The pEventErrorHandler object responsible for
        #  managing the errors.
        
        LDF.AEMcontributionIterator.__init__(self, event, contribution)
        self.TreeMaker    = treeMaker
        self.ErrorHandler = errorHandler

    ## @brief Handle error function overload
    #  Inspiration from the original c++ code implementation
    #  of the handleError function in "AEMcontributionIterator.cpp"
    #
    ##  return code is:
    #   - negative to indicate bail immediately
    #   - 0 for SUCCESS
    #   - positive to indicate that there was an error but iteration can continue
    #
    #	201 : 'ERR_TooManyPHAs'       # All AcceptMap bits were processed but end-of-PHA-list flag was not seen
    #	202 : 'ERR_TooFewPHAs'        # Not all AcceptMap bits were processed but end-of-PHA-list flag was seen
    #	203 : 'ERR_TimeOut'           # Time out
    #	204 : 'ERR_ParityErrorHeader' # Header parity error
    #	205 : 'ERR_ParityErrorPHA'    # PHA parity error
    #	206 : 'ERR_ExtraBytes'	      # AEM contribution has unexpected bytes after its end. 
    #	207 : 'ERR_Overrun'	      # The end of AEM contribution was found bytes beyond its claimed length.
    #	208 : 'ERR_NonZero'	      # Padding after AEM contribution is not MBZ as expected.
    #
    ## Error parameters : p1 = cable, p2 = channel
    #
    
    def handleError(self, event, code, p1, p2):

    	 if code == LDF.AEMcontributionIterator.ERR_TooManyPHAs:
             logger.debug("pha:ERR_TooManyPHAs\n"\
	                  "\tFor AEMcontribution cable %d, channel %d:\n"\
                          "\tAll AcceptMap bits were processed but\n"\
                          "\tend-of-PHA-list flag was not seen.\n"\
                          "\tParser may be lost.\n"% (p1, p2))
		   
	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Too Many PHAs', p1, p2])
	     
    	 # Details to be fixed, see C++ code
	 # p1 is the index of the header in the event contribution
	 # need to understand how to get the cable and the accept map from that
	 elif code == LDF.AEMcontributionIterator.ERR_TooFewPHAs: 
             logger.debug("pha:ERR_TooFewPHAs\n"\
	                  "\tFor AEMcontribution cable ?, channel %d:\n"\
                          "\tNot all AcceptMap bits were processed but\n"\
                          "\tend-of-PHA-list flag was seen.\n"\
                          "\tParser may be lost.\n"% (p2))
		      
	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Too Few PHAs', p1, p2])

#    	 elif code == LDF.AEMcontributionIterator.ERR_TimeOut:
#             logger.debug("pha:ERR_TimeOut\n"\
#	                  "\tFor AEMcontribution cable %d, channel %d:\n"\
#                          "\tTime Out\n" % (p1, p2))
#		   
#	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Time Out', p1, p2])

#    	 elif code == LDF.AEMcontributionIterator.ERR_ParityErrorHeader:
#             logger.debug("pha:ERR_ParityErrorHeader\n"\
#	                  "\tFor AEMcontribution cable %d, channel %d:\n"\
#                          "\tHeader Parity error detected.\n"\
#                          "\tParser may be lost.\n"% (p1, p2))
#		   
#	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Parity Error Header', p1, p2])

#    	 elif code == LDF.AEMcontributionIterator.ERR_ParityErrorPHA:
#             logger.debug("pha:ERR_ParityErrorPHA\n"\
#	                  "\tFor AEMcontribution cable %d, channel %d:\n"\
#                          "\tPHA Parity error detected.\n"\
#                          "\tParser may be lost.\n"% (p1, p2))
#		   
#	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Parity Error PHA', p1, p2])
 	     
    	 elif code == LDF.AEMcontributionIterator.ERR_ExtraBytes:
             logger.debug("pha:ERR_ExtraBytes\n"\
                          "\tAEM contribution has %d = 0x%04x "\
                          "\tunexpected bytes after its end\n"\
                          "\tParser may be lost.\n"% (p1, p1))
		   
	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Extra Bytes', p1, p2])

    	 elif code == LDF.AEMcontributionIterator.ERR_Overrun:
             logger.debug("pha:ERR_Overrun\n"\
	                  "\tThe end of AEM contribution was found %d = 0x%04x"\
                          "\tbytes beyond its claimed length\n"\
                          "\tParser may be lost.\n"% (p1, p1))
		   
	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Overrun', p1, p2])
	     
    	 elif code == LDF.AEMcontributionIterator.ERR_NonZero:
             logger.debug("pha:ERR_NonZero\n"\
	                  "\tPadding after AEM contribution is not MBZ as expected\n"
                          "\tParser may be lost.\n")
		   
	     self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['Non Zero'])

    	 else:
    	     logger.debug("UNKNOWN_ERROR\n"\
                          "\tUnrecognized error code %d = 0x%08x with "\
                          "\targuments %d = 0x%08x, %d = 0x%08x\n" %\
                          (code, code, p1, p1, p2, p2))

             self.ErrorHandler.fill('AEM_CONTRIB_ERROR', ['UNKNOWN_ERROR_CODE', p1, p2])

         return code

    def populateAcceptList(self, header):
        self.AcceptList = []
        acceptMap = header.acceptMap()
        for i in range(18):
            if (acceptMap >> i) & 0x1:
                self.AcceptList.append(17 - i)

    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
    #
       
    def header(self, cable, header):
        if header.parityError():
            self.ErrorHandler.fill('ACD_HEADER_PARITY_ERROR', [cable])
        self.populateAcceptList(header)
    
    ## @brief Function included by default by the corresponding method
    #  of the derived iterator (the one which is actually run).
    #
    
    def pha(self, cable, channel, pha):
        if channel not in self.AcceptList:
            self.ErrorHandler.fill('ACD_PHA_INCONSISTENCY',\
                                   [cable, channel, self.AcceptList])
        if pha.parityError():
            self.ErrorHandler.fill('ACD_PHA_PARITY_ERROR', [cable, channel])

    ## @brief Fill acd_tile_count tree branch.
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param channel
    #  The tile channel id.
    ## @param pha
    #  The tile pulse height.

    def acd_tile_count__pha__(self, cable, channel, pha):
	self.TreeMaker.getVariable('acd_tile_count')[0] += 1

    ## @brief Fill acd_tile_hitmap tree branch.
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param header
    #  The contribution header.
   
    def acd_tile_hitmap__header__(self, cable, header):
	self.TreeMaker.getVariable('acd_tile_hitmap')[0] = header.hitMap()

    ## @brief Fill AcdHitChannel tree branch [12,18].
    ## @param self
    #  The class instance.
    ## @param cable
    #  The tile cable id.
    ## @param channel
    #  The tile channel id.
    ## @param pha
    #  The tile pulse height.

    def AcdHitChannel__pha__(self, cable, channel, pha):
	self.TreeMaker.getVariable('AcdHitChannel')[cable][channel] += 1

