#! /bin/env python

import os
import sys
import time
import logging
import LDF
import ROOT
import logging

from copy 			      import copy
from array                            import array
from LICOS_Scripts.analysis.LsfMerger import LsfMerger
from pRootTreeMaker                   import pRootTreeMaker
from pLATdatagramIterator             import pLATdatagramIterator
from pLATcontributionIterator         import pLATcontributionIterator
from pEBFeventIterator                import pEBFeventIterator
from pXmlParser                       import pXmlParser
from pGlobals			      import *
from pContributionIteratorWriter      import *
from pContributionWriter              import *

logging.basicConfig(level=logging.DEBUG)

class pDataProcessor:

    def __init__(self, configFilePath, inputFilePath, outputFilePath):
        if outputFilePath is None:
            outputFilePath = '%s.root' % inputFilePath.split('.')[0]
        self.__XmlParser = pXmlParser(configFilePath)
        self.TreeMaker   = pRootTreeMaker(self.__XmlParser, outputFilePath)
        self.__updateContributionIterators()
        self.__updateContributions()
        from pLATcomponentIterator    import pLATcomponentIterator
        self.lci         = pLATcomponentIterator(self.TreeMaker)
        self.eei         = pEBFeventIterator(self.lci)
        self.lcti        = pLATcontributionIterator(self.eei)
        self.ldi         = pLATdatagramIterator(self.lcti)
        self.ldbi        = LDF.LATdataBufferIterator(self.ldi)
        self.NumEvents   = 0
        self.LsfMerger   = None
        self.OutROOTFile = None
        self.ROOTTree    = None
        self.openFile(inputFilePath)
	self.TimeHackRollOverNum = 0
	self.TimeHackHasJustRolledOver = False

    def openFile(self, filePath):
        logging.info('Opening the input data file...')
        if os.path.exists(filePath):
            self.LsfMerger   = LsfMerger(filePath)
            logging.info('Done.')
        else:
            sys.exit('Input data file not found. Exiting...')

    def __updateContributionIterators(self):
        writer = pTKRcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()
        writer = pCALcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()

    def __updateContributions(self):
        writer = pGEMcontributionWriter(self.__XmlParser)
        writer.writeComponent()

    def processEvent(self, event):
	self.TreeMaker.resetVariables()
	self.ldbi.iterate(event, len(event))
        self.TreeMaker.fillTree()
        self.NumEvents += 1
        if not self.NumEvents%100:
            logging.debug('%d events processed' % self.NumEvents)
        
    def processMetaEvent(self, meta):
	self.TreeMaker.DefaultVariablesDictionary['event_timestamp'][0] = \
             self.calculateTimeStamp(meta)
	#print meta.context().run().startedAt()
	#print meta.context().run().id()
	#print meta.context().scalers().livetime()
	#print meta.context().open().crate()

    def calculateTimeStamp(self, meta):
	timeTics = copy(meta.timeTics())
	timeHack_tics = copy(meta.timeHack().tics())
	timeHack_hacks = copy(meta.timeHack().hacks())
	clockTicksEvt1PPS = timeTics - timeHack_tics	
	if(clockTicksEvt1PPS <0):
	    clockTicksEvt1PPS += CLOCK_ROLLOVER

	#Check for timeHack rollover
	hPrevious = meta.context().previous().timeHack().hacks()
	hCurrent  = meta.context().current().timeHack().hacks()
	if (hCurrent - hPrevious < 0) and not self.TimeHackHasJustRolledOver :
	    self.TimeHackRollOverNum += 1
	    self.TimeHackHasJustRolledOver = True
	if hCurrent - hPrevious > 0:
	   self.TimeHackHasJustRolledOver = False
	
	timestamp = 128*self.TimeHackRollOverNum + timeHack_hacks +  clockTicksEvt1PPS*CLOCK_TIC
	return timestamp

    def startProcessing(self, maxEvents = 1000):
        logging.info('Beginning data processing...')
        startTime = time.time()
        while (self.NumEvents != maxEvents):
            try:
                (meta, buff) = self.LsfMerger.getUncompressedEvent()
            except TypeError:
                logging.info('End of file reached.')
                break
            self.processMetaEvent(meta)
            self.processEvent(buff)
        elapsedTime = time.time() - startTime
        averageRate = self.NumEvents/elapsedTime
        logging.info('Done. %d events processed in %s s (%f Hz).\n' %\
                     (self.NumEvents, elapsedTime, averageRate))
        self.TreeMaker.close()

     

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',\
                      default='../xml/config.xml', type=str,   \
                      help='path to the input xml configuration file')
    parser.add_option('-n', '--num-events', dest='events',      \
                      default=-1, type=int,       \
                      help='number of events to be processed')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default='IsocDataFile.root', type=str,
                      help='path to the output ROOT file')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    
    dataProcessor  = pDataProcessor(options.config_file, args[0],\
                                    options.output_file)
    dataProcessor.startProcessing(options.events)
