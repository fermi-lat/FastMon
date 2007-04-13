
import time
import sys
import cPickle
import logging
import pUtils

from pConfig import *
from pError  import pError


MAX_DETAILED_LIST_LENGTH  = 10
BASE_STRING_FORMAT_LENGTH = 40

class pErrorHandler:

    def __init__(self, pickleFilePath=None):
        self.__EventNumber = None
        self.__ErrorsList  = []
        if pickleFilePath is not None:
            self.load(pickleFilePath)
            
    def load(self, inputFilePath):
        logging.info('Unpickling the error handler from %s...' % inputFilePath)
        startTime = time.time()
        self.__ErrorsList = cPickle.load(file(inputFilePath, 'r'))
        logging.info('Done in %s s.\n' % (time.time() - startTime))
        
    def dump(self, outputFilePath):
        logging.info('Pickling the error handler into %s...' % outputFilePath)
        startTime = time.time()
        cPickle.dump(self.__ErrorsList, file(outputFilePath, 'w'))
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    def setEventNumber(self, eventNumber):
        self.__EventNumber = eventNumber

    def fill(self, errorCode, parameters=[]):
        error = pError(self.__EventNumber, errorCode, parameters)
        self.__ErrorsList.append(error)

    def getError(self, index):
        try:
            return self.__ErrorsList[index]
        except IndexError:
            logging.error('Error index (%d) out of range (0-%d)' %\
                          (index, self.getTotalNumErrors()))

    def getErrorCodesList(self):
        errorCodesList = []
        for error in self.__ErrorsList:
            errorCode = error.ErrorCode
            if errorCode not in errorCodesList:
                errorCodesList.append(errorCode)
        return errorCodesList

    def getTotalNumErrors(self):
        return len(self.__ErrorsList)

    def getNumErrors(self, errorCode):
        numErrors = 0
        for error in self.__ErrorsList:
            if error.ErrorCode == errorCode:
                numErrors += 1
        return numErrors

    def getTotalNumBadEvents(self):
        eventsList = []
        for error in self.__ErrorsList:
            eventNumber = error.EventNumber
            if eventNumber not in eventsList:
                eventsList.append(eventNumber)
        return len(eventsList)

    def getNumBadEvents(self, errorCode):
        eventsList = []
        for error in self.__ErrorsList:
            eventNumber = error.EventNumber
            if eventNumber not in eventsList and error.ErrorCode == errorCode:
                eventsList.append(eventNumber)
        return len(eventsList)

    def __printEventHeader(self, eventNumber):
        print '********   Event %d   ********' % eventNumber

    def browseErrors(self):
        logging.info('Starting error browser...')
        numErrors = self.getTotalNumErrors()
        if numErrors  == 0:
            logging.info('There are no errors.')
            sys.exit()
        print
        errorIndex  = 0
        eventNumber = self.getError(0).EventNumber
        self.__printEventHeader(eventNumber)
        while(errorIndex < numErrors):
            error = self.getError(errorIndex)
            if error.EventNumber != eventNumber:
                eventNumber = error.EventNumber
                message = 'Press q to quit, any other key to continue\n'
                if raw_input(message) == 'q':
                    sys.exit()
                self.__printEventHeader(eventNumber)
            print error.getPlainRepresentation(False),
            errorIndex += 1
        print
        logging.info('There are no more errors.\n')

    def getPlainSummary(self):
        errorCodesList = self.getErrorCodesList()
        numErrors      = self.getTotalNumErrors()
        numBadEvents   = self.getTotalNumBadEvents()
        output = '** Error counter summary **\n\n'
        if numErrors == 0:
            output += 'No errors found in this run.\n'
        else:
            output += '-- Summary by event number\n\n'
            output += '%s: %d\n' %\
               (pUtils.expandString('Total number of events with errors',\
                                    BASE_STRING_FORMAT_LENGTH), numBadEvents)
            for errorCode in errorCodesList:
                output += pUtils.expandString('Number of events with %s' %\
                                              errorCode,\
                                              BASE_STRING_FORMAT_LENGTH)
                output += ': %d\n' % self.getNumBadEvents(errorCode)
            output += '\n'
            output += '-- Summary by error code\n\n'
            output += '%s: %d\n' %\
                      (pUtils.expandString('Total number of errors',\
                                           BASE_STRING_FORMAT_LENGTH),\
                       numErrors)
            for errorCode in errorCodesList:
                output += pUtils.expandString('Number of %s errors' %\
                                              errorCode,\
                                              BASE_STRING_FORMAT_LENGTH)
                output += ': %d\n' % self.getNumErrors(errorCode)
            output += '\n'
            output += '-- Detailed list by event (max %d events)\n\n' %\
                      MAX_DETAILED_LIST_LENGTH
            errorIndex   = 0
            maxNumEvents = min(numBadEvents, MAX_DETAILED_LIST_LENGTH)
            eventNumber  = self.getError(0).EventNumber
            output += '+ Event %d\n' % eventNumber
            numEvents    = 1
            while(numEvents < maxNumEvents):
                error = self.getError(errorIndex)
                if error.EventNumber != eventNumber:
                    eventNumber = error.EventNumber
                    numEvents += 1
                    output    += '\n+ Event %d\n' % eventNumber
                output     += error.getPlainRepresentation(False)
                errorIndex += 1
            output += error.getPlainRepresentation(False)
        return output

    def getDoxygenSummary(self):
        errorCodesList = self.getErrorCodesList()
        numErrors      = self.getTotalNumErrors()
        numBadEvents   = self.getTotalNumBadEvents()
        output = '\n@section errors_summary Error statistics summary\n'
        if numErrors == 0:
            output += 'No errors have been found in this run.\n'
        else:
            output += '\n@subsection summary_by_evt ' +\
                      'Summary by event number\n\n'
            output += '@li Total number of events with errors: %d\n' %\
                      numBadEvents
            for errorCode in errorCodesList:
                output += '@li Number of events with %s errors: %d\n' %\
                          (pUtils.verbatim(errorCode),\
                           self.getNumBadEvents(errorCode))
            output += '\n@subsection summary_by_code Summary by error code\n\n'
            output += '@li Total number of errors: %d\n' % numErrors
            for errorCode in errorCodesList:
                output += '@li Number of %s errors: %d\n' %\
                          (pUtils.verbatim(errorCode),\
                           self.getNumErrors(errorCode))
            output += '\n@subsection detailed_summary ' +\
                      'Detailed summary (max %d events)\n\n' %\
                      MAX_DETAILED_LIST_LENGTH
            errorIndex   = 0
            maxNumEvents = min(numBadEvents, MAX_DETAILED_LIST_LENGTH)
            eventNumber  = self.getError(0).EventNumber
            output += '@li Event %d\\n\n' % eventNumber
            numEvents    = 1
            while(numEvents < maxNumEvents):
                error = self.getError(errorIndex)
                if error.EventNumber != eventNumber:
                    eventNumber = error.EventNumber
                    numEvents += 1
                    output    += '\n+ Event %d\n' % eventNumber
                output     += error.getDoxygenRepresentation()
                errorIndex += 1
            output += error.getDoxygenRepresentation()
        return '%s\n\n' % output

    def writeDoxygenSummary(self, filePath):
        logging.info('Writing the error file for the report...')
        startTime   = time.time()
        fileContent = self.getDoxygenSummary()
        file(filePath, 'w').writelines(fileContent)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    def __str__(self):
        return self.getPlainSummary()

        

if __name__ == '__main__':
    handler = pErrorHandler()
    handler.setEventNumber(10)
    for i in range(3):
        handler.fill('GTCC_FIFO_ERROR', [12, i, 0x32])
    handler.setEventNumber(34)
    handler.fill('GTCC_TIMEOUT_ERROR', [3, 1, 'hello'])
    handler.fill('GTFE_PHASE_ERROR', [2, 8, 5, 1, 2, 3, 4, 5])
    handler.setEventNumber(101)
    for i in range(2):
        handler.fill('GTCC_TIMEOUT_ERROR', [12, i, 0x32])
    print handler
    print handler.getDoxygenSummary()
    #handler.dump('test.errors.pickle')
    #newHandler = pErrorHandler('test.errors.pickle')
    #newHandler.browseErrors()
