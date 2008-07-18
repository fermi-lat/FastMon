#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pErrorHandler')

import time
import sys
import cPickle
import pUtils

from pError      import pError
from pErrorEvent import pErrorEvent

MAX_ERROR_EVENTS = 500

class pErrorHandler:

    def __init__(self, pickleFilePath = None):
        self.NumProcessedEvents = 'n/a'
        self.ErrorCountsDict = {}
        self.ErrorEventsDict = {}
        self.ErrorsBuffer = []
        if pickleFilePath is not None:
            self.load(pickleFilePath)
            
    def load(self, inputFilePath):
        logger.info('Unpickling the error handler from %s...' % inputFilePath)
        startTime = time.time()
        (self.ErrorCountsDict, self.ErrorEventsDict) =\
                                cPickle.load(file(inputFilePath, 'r'))
        logger.info('Done in %.4f s.\n' % (time.time() - startTime))
        
    def dump(self, outputFilePath):
        logger.info('Pickling the error handler into %s...' % outputFilePath)
        startTime = time.time()
        cPickle.dump((self.ErrorCountsDict, self.ErrorEventsDict),\
                     file(outputFilePath, 'w'))
        logger.info('Done in %.4f s.\n' % (time.time() - startTime))


    def fill(self, errorCode, parameters=[]):
        error = pError(errorCode, parameters)
        # fill the summary by error code
        try:
            self.ErrorCountsDict[errorCode] += 1
        except KeyError:
            self.ErrorCountsDict[errorCode] = 1
        # fill a buffer of errors for this event.
        self.ErrorsBuffer.append(error)
        

    def flushErrorsBuffer(self, eventNumber):
        # fill the ErrorEventsDict, in case the event has errors,
        # using the correct event ID
        # to be called at the end of event processing
        if self.ErrorsBuffer != []:
            errorEvent = pErrorEvent(eventNumber)
            for error in self.ErrorsBuffer:
                errorEvent.addError(error)
            self.ErrorEventsDict[eventNumber] = errorEvent
            self.ErrorsBuffer = []
            return errorEvent.ErrorSummary
        return 0

    def getNumErrors(self):
        return sum(self.ErrorCountsDict.values())

    def getNumErrorEvents(self):
        return len(self.ErrorEventsDict)
            
    def browseErrors(self):
        if self.getNumErrors() == 0:
            logger.info('No errors found in this file.')
            sys.exit()
        logger.info('%d events with errors (%d errors in total) found.' %\
                    (self.getNumErrorEvents(), self.getNumErrors()))
        logger.info('Starting error browser...\n')
        errorEventsList = self.ErrorEventsDict.keys()
        errorEventsList.sort()
        for eventNumber in errorEventsList:
            print self.ErrorEventsDict[eventNumber]
            message = 'Press q to quit, any other key to continue\n'
            if raw_input(message) == 'q':
                sys.exit()
        logger.info('There are no more errors.\n')

    def writeXmlOutput(self, filename):
        try:
            from pXmlWriter import pXmlWriter
        except:
            logger.error("Can not find pXmlWriter module. Exit.")
            return None
        truncated = self.getNumErrorEvents() > MAX_ERROR_EVENTS
        xmlWriter  = pXmlWriter(filename)
        xmlWriter.openTag('errorContribution')
        xmlWriter.indent()
        xmlWriter.newLine()
        xmlWriter.writeComment('Summary by error code')
        xmlWriter.openTag('errorSummary')
        xmlWriter.indent()
        for (code, number) in self.ErrorCountsDict.items():
            xmlWriter.writeTag('errorType', {'code':code, 'quantity': number })
        xmlWriter.backup()
        xmlWriter.closeTag('errorSummary')
        xmlWriter.newLine()
        xmlWriter.writeComment('Summary by event number')
        xmlWriter.openTag('eventSummary',\
                          {'num_error_events'      : self.getNumErrorEvents(),
                           'num_processed_events'  : self.NumProcessedEvents,
                           'truncated'             : truncated})
        xmlWriter.indent()
        errorEventNumbers = self.ErrorEventsDict.keys()
        errorEventNumbers.sort()
        for eventNumber in errorEventNumbers[:MAX_ERROR_EVENTS]:
            errorEvent = self.ErrorEventsDict[eventNumber]
            xmlWriter.openTag('errorEvent', {'eventNumber': eventNumber})
            xmlWriter.indent()
            for error in errorEvent.ErrorsList:
                xmlWriter.writeLine(error.getXmlLine())
            xmlWriter.backup()
            xmlWriter.closeTag('errorEvent')
        xmlWriter.backup()
        xmlWriter.closeTag('eventSummary')
        xmlWriter.backup()
        xmlWriter.newLine()
        xmlWriter.closeTag('errorContribution')
        xmlWriter.closeFile()


        

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog pickle_file')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    errorHandler = pErrorHandler(args[0])
    errorHandler.browseErrors()
