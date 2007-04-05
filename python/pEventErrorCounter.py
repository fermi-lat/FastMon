## @package pEventErrorCounter
## @brief Includes all the tools to keep track of the events with error in
#  the data run.

import pUtils
import time
import logging

## @brief Implementation of an error counter.
#
#  The statistics of the errors is implemented as a pyhton dictionary in which
#  the errors themselves are indexed based on their error code.
#  This approach is flexible in that it is not necessary to know all the error
#  codes in advance.
#  The counter is filled by a suitable event iterator using the
#  fill() method, which requires the error code as a parameter, and in case no
#  errors of that type have been detected, yet, the error code is added to the
#  keys of the dictionary.
## @todo Implement support for error counting at the event level.

class pEventErrorCounter:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    
    def __init__(self):

        ## @var __Counter
        ## @brief Basic python dictionary underlying the error counter.
        #
        #  It is intended to include all the errors, indexed by a code
        #  identifying the error type.
        
        self.__Counter = {}

    ## @brief Reset the error counter.
    #
    #  It essentially reset the pyhton dictionary @ref __Counter.
    ## @param self
    #  The class instance.

    def reset(self):
        self.__Counter = {}

    ## @brief Fill the error counter.
    #
    #  If the counter already contains errors with the same code, then the
    #  counter value for that particular code is incremented by 1. It is set
    #  to 1 otherwise.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.

    def fill(self, errorCode):
        try:
            self.__Counter[errorCode] += 1
        except KeyError:
            self.__Counter[errorCode] = 1

    ## @brief Return the number of errors corresponding to a particular
    #  error code.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.

    def getNumErrors(self, errorCode):
        try:
            return self.__Counter[errorCode]
        except KeyError:
            return 0

    ## @brief Return the number of errors for a particular error code,
    #  along with the error code itself, nicely formatted to be printed
    #  on the screen.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.
    
    def getFormattedNumErrors(self, errorCode):
        return '%s: %d\n' % (pUtils.expandString(errorCode, 30),\
                             self.getNumErrors(errorCode))

    ## @brief Return the error counter summary, nicely formatted to be printed
    #  on the screen.
    ## @param self
    #  The class instance.
    
    def getFormattedSummary(self):
        summary = '** Event errors counter summary **\n'
        if self.__Counter == {}:
            summary += 'No errors found in this run.\n'
        else:
            for errorCode in self.__Counter.keys():
                summary += self.getFormattedNumErrors(errorCode)
        return summary

    ## @brief Return the error counter summary, in a doxygen-like fashion,
    #  to be included in the report.
    ## @param self
    #  The class instance.

    def getDoxygenFormattedSummary(self):
        summary = '\n@section errors_summary Error statistics summary\n\n'
        if self.__Counter == {}:
            summary += 'No errors have been found in this run.\n'
        else:
            for errorCode in self.__Counter.keys():
                summary += ('@li There are %d events with '+\
                            '@code%s@endcode errors.\n')   %\
                            (self.getNumErrors(errorCode), errorCode)
        return '%s\n\n' % summary

    ## @brief Write the doxygen summary to a file, to be included in the
    #  report at a later stage.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The output file path.
    
    def writeDoxygenFormattedSummary(self, filePath):
        logging.info('Writing the errors file for the report...')
        startTime = time.time()
        file(filePath, 'w').writelines(self.getDoxygenFormattedSummary())
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Class representation.
    ## @param self
    #  The class instance.
    
    def __str__(self):
        return self.getFormattedSummary()


if __name__ == '__main__':
    counter = pEventErrorCounter()
    print counter
    for i in range(10):
        counter.fill('GTRC FIFO full')
    for i in range(3):
        counter.fill('GTCC timeout')
    counter.fill('GTFE phasing error')
    print counter
    counter.writeDoxygenFormattedSummary('test.errors')
