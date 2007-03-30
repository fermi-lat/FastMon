## @package pEventErrorCounter
## @brief Includes all the tools to keep track of the events with error in
#  the data run.


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
    ## @todo use pUtils functions here.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.
    
    def getFormattedNumErrors(self, errorCode, codeLength=30):
        numSpaces = max((codeLength - len(errorCode)), 0)
        return '%s%s: %d\n' % (errorCode, ' '*numSpaces,\
                               self.getNumErrors(errorCode))

    ## @brief Class representation.
    ## @param self
    #  The class instance.
    
    def __str__(self):
        out = '** Event errors counter statistics **\n'
        if self.__Counter == {}:
            out += 'No errors found in this run.\n'
        else:
            for errorCode in self.__Counter.keys():
                out += self.getFormattedNumErrors(errorCode)
        return out


if __name__ == '__main__':
    counter = pEventErrorCounter()
    print counter
    for i in range(10):
        counter.fill('GTRC FIFO full')
    for i in range(3):
        counter.fill('GTCC timeout')
    counter.fill('GTFE phasing error')
    print counter
