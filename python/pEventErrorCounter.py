## @package pEventErrorCounter
## @brief Includes all the tools to keep track of the events with error in
#  the data run.

import pUtils
import time
import logging

## @brief Implementation of an error counter.

class pEventErrorCounter:

    __FORMAT_LENGTH = 40

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    
    def __init__(self):
        
        ## @var
        ## @brief

        ## @var
        ## @brief

        ## @var
        ## @brief 

        self.__EventNumber     = None
        self.__CodeErrorsDict  = {}
        self.__EventErrorsDict = {}

    ## @brief Reset the error counter.
    ## @param self
    #  The class instance.

    def reset(self):
        self.__EventNumber     = None
        self.__CodeErrorsDict  = {}
        self.__EventErrorsDict = {}
        
    ## @brief Set the current event number.
    ## @param self
    #  The class instance.
    ## @param eventNumber
    #  The event number.

    def setEventNumber(self, eventNumber):
        self.__EventNumber = eventNumber

    def fill(self, errorCode):
        self.__fillCodeErrorsDict(errorCode)
        self.__fillEventErrorsDict(errorCode)        

    def __fillCodeErrorsDict(self, errorCode):
        if errorCode not in self.__CodeErrorsDict.keys():
            self.__CodeErrorsDict[errorCode] = 1
        else:
            self.__CodeErrorsDict[errorCode] += 1
            
    def __fillEventErrorsDict(self, errorCode):
        if self.__EventNumber not in self.__EventErrorsDict.keys():
            self.__EventErrorsDict[self.__EventNumber] = {}
        try:
            self.__EventErrorsDict[self.__EventNumber][errorCode] += 1
        except KeyError:
            self.__EventErrorsDict[self.__EventNumber][errorCode] = 1

    ## @brief Return the number of events with errors of a particular
    #  type.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.

    def getNumErrorEvents(self, errorCode):
        numEvents = 0
        for dict in self.__EventErrorsDict.values():
            if errorCode in dict.keys():
                numEvents += 1
        return numEvents

    ## @brief Return the total number of events with errors (of any type).
    ## @param self
    #  The class instance.

    def getTotalNumErrorEvents(self):
        return len(self.__EventErrorsDict)

    def getDetailedErrorEventsDict(self):
        errorEventsDict = {}
        for errorCode in self.__CodeErrorsDict.keys():
            errorEventsDict[errorCode] = 0
        for eventNumber in self.__EventErrorsDict.keys():
            for errorCode in self.__EventErrorsDict[eventNumber].keys():
                errorEventsDict[errorCode] += 1
        return errorEventsDict

    ## @brief Return the number of errors of a particular type.
    ## @param self
    #  The class instance.
    ## @param errorCode
    #  The The error code.

    def getNumErrors(self, errorCode):
        return self.__CodeErrorsDict[errorCode]

    ## @brief Return the total number of errors (of any type).
    ## @param self
    #  The class instance.

    def getTotalNumErrors(self):
        return sum(self.__CodeErrorsDict.values())

    def getFormattedTotalNumErrorEvents(self):
        output = 'Total number of events with errors'
        return '%s: %d\n' % (pUtils.expandString(output,\
                                                 self.__FORMAT_LENGTH),\
                             self.getTotalNumErrorEvents())

    def getFormattedErrorEventSummary(self, eventNumber):
        output = '    Event number'
        output = '%s: %d\n' % (pUtils.expandString(output,\
                                                   self.__FORMAT_LENGTH),\
                               eventNumber)
        for errorCode in self.__EventErrorsDict[eventNumber].keys():
            output += pUtils.expandString('        %s' % errorCode,\
                                          self.__FORMAT_LENGTH)
            output += ': %d\n' % self.__EventErrorsDict[eventNumber][errorCode]
        return output

    def getFormattedErrorEventsList(self, detailed=True):
        output = '%s' % self.getFormattedTotalNumErrorEvents()
        output += self.getFormattedDetailedErrorEventsDict()
        if detailed:
            output += '\nDetails:\n'
            for eventNumber in self.__EventErrorsDict.keys():
                output += '%s\n' %\
                          self.getFormattedErrorEventSummary(eventNumber)
        return output

    def getFormattedDetailedErrorEventsDict(self):
        output = ''
        detailedErrorEventsDict = self.getDetailedErrorEventsDict()
        for (errorCode, numEvents) in detailedErrorEventsDict.items():
            output += pUtils.expandString('Events with %s' % errorCode,\
                                          self.__FORMAT_LENGTH)
            output += ': %d\n' % numEvents
        return output

    def getFormattedTotalNumErrors(self):
        output = 'Total number of errors'
        return '%s: %d\n' % (pUtils.expandString(output,\
                                                 self.__FORMAT_LENGTH),\
                             self.getTotalNumErrors())

    def getFormattedErrorCodesList(self):
        output = '%s' % self.getFormattedTotalNumErrors()
        for (errorCode, numEvents) in self.__CodeErrorsDict.items():
            output += pUtils.expandString('Number of %s errors' % errorCode,\
                                          self.__FORMAT_LENGTH)
            output += ': %d\n' % numEvents
        return output

    def getFormattedSummary(self, detailed=True):
        output = '** Error counter summary **\n\n'
        if self.getTotalNumErrors() == 0:
            output += 'No errors found in this run.\n'
        else:
            output += '-- Summary by event number:\n\n'
            output += self.getFormattedErrorEventsList(detailed)
            output += '-- Summary by error code:\n\n'
            output += self.getFormattedErrorCodesList()
        return output

    ## @brief Return the error counter summary, in a doxygen-like fashion,
    #  to be included in the report.
    ## @param self
    #  The class instance.

    def getDoxygenFormattedSummary(self):
        output = '\n@section errors_summary Error statistics summary\n\n'
        if self.getTotalNumErrors() == 0:
            output += 'No errors have been found in this run.\n'
        else:
            output += 'Doxygen summary to be implemented\n'
        return '%s\n\n' % output

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

##     def getDoxygenFormattedSummary(self):
##         summary = '\n@section errors_summary Error statistics summary\n\n'
##         if self.__Counter == {}:
##             summary += 'No errors have been found in this run.\n'
##         else:
##             for errorCode in self.__Counter.keys():
##                 summary += ('@li There are %d events with '+\
##                             '@code%s@endcode errors.\n')   %\
##                             (self.getNumErrors(errorCode), errorCode)
##         return '%s\n\n' % summary





if __name__ == '__main__':
    counter = pEventErrorCounter()
    counter.setEventNumber(10)
    for i in range(3):
        counter.fill('GTRC FIFO full')
    counter.setEventNumber(34)
    counter.fill('GTCC timeout')
    counter.fill('GTFE phasing error')
    print counter

