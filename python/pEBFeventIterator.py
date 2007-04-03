## @package pEBFeventIterator
## @brief Package managing the interation over EBF events.

import logging
import LDF


## @brief Implementation of the EBF event iterator.

class pEBFeventIterator(LDF.LDBI_EBFeventIterator):

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param latComponentIterator
    #  The LAT component iterator object.

    def __init__(self, latComponentIterator):

        ## @var __LatComponentIterator
        ## @brief The LAT component iterator object.

        LDF.LDBI_EBFeventIterator.__init__(self, latComponentIterator)
        self.__LatComponentIterator = latComponentIterator

    ## @brief Handle EBF event iterator errors.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
    ## @param code
    #  The error code.
    ## @param p1
    #  Parameter 1.
    ## @param p2
    #  Parameter 2.

    def handleError(self, event, code, p1, p2):
        fn = 'pEBFeventIterator.handleError()'
        if code == LDF.EBFeventIterator.ERR_NonEBFevent:
            logging.error('%s: non-EBF event contribution.' % fn)
            return 1
        else:
            logging.error('%s: unknown error code.' % fn)
            return 0

    ## @brief Process the event.
    ## @param self
    #  The class instance.
    ## @param evt
    #  The event object.
    
    def process(self, evt):
        if evt.status() != 0:
            fn = 'pEBFeventIterator.process()'
            logging.error('%s: bad status in event header.')
            return evt.status()
        else:
            self.__LatComponentIterator.iterate(evt)
            return self.__LatComponentIterator.status()
