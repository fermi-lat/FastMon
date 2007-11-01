#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pErrorHandler')

import time
import sys
import cPickle
import pUtils

from pError      import pError
from pErrorEvent import pErrorEvent

MAX_DETAILED_LIST_LENGTH  = 100

class pErrorHandler:

    def __init__(self, pickleFilePath=None):
        self.EventNumber     = None
        self.ErrorCountsDict = {}
        self.ErrorEventsDict = {}
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

    def setEventNumber(self, eventNumber):
        self.EventNumber = eventNumber

    def fill(self, errorCode, parameters=[]):
        error = pError(errorCode, parameters)
        try:
            self.ErrorCountsDict[errorCode] += 1
        except KeyError:
            self.ErrorCountsDict[errorCode] = 1
        try:
            self.ErrorEventsDict[self.EventNumber].addError(error)
        except KeyError:
            self.ErrorEventsDict[self.EventNumber] =\
                                      pErrorEvent(self.EventNumber)
            self.ErrorEventsDict[self.EventNumber].addError(error)

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
        xmlWriter  = pXmlWriter(filename)
        xmlWriter.openTag('errorContribution')
        xmlWriter.indent()
        xmlWriter.writeComment('Summary by error code')
        xmlWriter.openTag('errorSummary')
        xmlWriter.indent()
        for (code, number) in self.ErrorCountsDict.items():
            xmlWriter.writeTag('errorType', {'code':code, 'quantity': number })
        # write stuff here
        xmlWriter.backup()
        xmlWriter.closeTag('errorSummary')
        xmlWriter.backup()
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
