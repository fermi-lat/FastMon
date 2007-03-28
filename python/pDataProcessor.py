#! /bin/env python

## @package pDataProcessor
## @brief Basic module for data processing.

import os
import sys
import time
import logging
import LDF
import ROOT
import logging
import struct

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
from pMetaEventProcessor	      import *
from pEventErrorCounter               import pEventErrorCounter

logging.basicConfig(level=logging.DEBUG)


## @brief The data processor implementation.

class pDataProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param configFilePath
    #  Path to the xml configuration file path.
    ## @param inputFilePath
    #  Path to the input raw data file.
    ## @param outputFilePath
    #  Path to the output ROOT file.

    def __init__(self, configFilePath, inputFilePath, outputFilePath=None):

        ## @var __XmlParser
        ## @brief The xml parser object (pXmlParser instance).

        ## @var TreeMaker
        ## @brief The tree maker object (pRootTreeMaker instance).

        ## @var ErrorCounter
        ## @brief The error counter object (pEventErrorCounter instance).

        ## @var MetaEventProcessor
        ## @brief The meta event processor (pMetaEventProcessor instance)

        ## @var LatCompIter
        ## @brief The LAT component iterator.

        ## @var EbfEventIter
        ## @brief The EBF event iterator.

        ## @var LatContrIter
        ## @brief The LAT contribution iterator.

        ## @var LatDatagrIter
        ## @brief The LAT datagram iterator.

        ## @var LatDataBufIter
        ## @brief The LAT data buffer iterator.

        ## @var NumEvents
        ## @brief The number of events processed by the data processor
        #  at a given time.

        ## @var LsfMerger
        ## @brief The lsf merger object (relevant for lsf data format only).

        ## @var LdfFile
        ## @brief The ldf file object (relevant for ldf data only). 

        ## @var StartTime
        ## @brief The data processor start time.

        ## @var StopTime
        ## @brief The data processor stop time.
        
        if outputFilePath is None:
            outputFilePath = '%s.root' % inputFilePath.split('.')[0]
        self.__XmlParser  = pXmlParser(configFilePath)
        self.TreeMaker    = pRootTreeMaker(self.__XmlParser, outputFilePath)
        self.ErrorCounter = pEventErrorCounter()
	self.MetaEventProcessor = pMetaEventProcessor(self.TreeMaker)	
        self.__updateContributionIterators()
        self.__updateContributions()
        from pLATcomponentIterator    import pLATcomponentIterator
        self.LatCompIter    = pLATcomponentIterator(self.TreeMaker,\
                                                    self.ErrorCounter)
        self.EbfEventIter   = pEBFeventIterator(self.LatCompIter)
        self.LatContrIter   = pLATcontributionIterator(self.EbfEventIter)
        self.LatDatagrIter  = pLATdatagramIterator(self.LatContrIter)
        self.LatDataBufIter = LDF.LATdataBufferIterator(self.LatDatagrIter)
        self.NumEvents      = None
        self.LsfMerger      = None
        self.LdfFile        = None
        self.StartTime      = None
        self.StopTime       = None
        self.openFile(inputFilePath)

    ## @brief Update the event contribution iterators, based on the xml
    #  configuration file.
    ## @param self
    #  The class instance.

    def __updateContributionIterators(self):
        writer = pTKRcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()
        writer = pCALcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()
        writer = pAEMcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()

    ## @brief Update the event contributions, based on the xml
    #  configuration file.
    ## @param self
    #  The class instance.

    def __updateContributions(self):
        writer = pGEMcontributionWriter(self.__XmlParser)
        writer.writeComponent()

    ## @brief Open the input raw data file.
    #
    #  Both ldf and lsf data files are supported at this level.
    #  The data type is identified based on the file extension.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  Path to the raw data file.
    
    def openFile(self, filePath):
        logging.info('Opening the input data file...')
        if os.path.exists(filePath):
	    fileType = filePath.split('.')[-1]
	    if fileType == 'lsf':
                self.LsfMerger   = LsfMerger(filePath)
	    elif fileType == 'ldf':
	        self.LdfFile = file(filePath, 'rb')
	    else:
	    	sys.exit('Unknown file type (%s).' % fileType)
            logging.info('Done.')
        else:
            sys.exit('Input data file not found. Exiting...')

    ## @brief Start the data processing.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events to be processed (default is -1, meaning
    #  the whole file).

    def start(self, maxEvents=-1):
        self.NumEvents = 0
        self.StartTime = time.time()
        if self.LsfMerger is not None:
	    self.startLSFProcessing(maxEvents)
	elif self.LdfFile is not None:
	    self.startLDFProcessing(maxEvents)
	else:
	    sys.exit('If you see this message, something went really bad...')
            logging.info('Starting data processing...')

    ## @brief Finalize the data processing.
    #
    #  This involves creating the histogram from the ROOT tree and
    #  printing out the statistics of the events with errors.
    ## @param self
    #  The class instance.
    
    def finalize(self):
        self.StopTime = time.time()
        elapsedTime   = self.StopTime - self.StartTime
        averageRate   = self.NumEvents/elapsedTime
        logging.info('Done. %d events processed in %s s (%f Hz).\n' %\
                     (self.NumEvents, elapsedTime, averageRate))
        self.TreeMaker.close()
        print self.ErrorCounter

    ## @brief Process an event.
    #
    #  This is actually called both for lsf and ldf files.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
 
    def processEvent(self, event):
	self.LatDataBufIter.iterate(event, len(event))
        label = 'processor_event_number'
        self.TreeMaker.VariablesDictionary[label][0] = self.NumEvents
        self.NumEvents += 1
        if not self.NumEvents % 100:
            logging.debug('%d events processed' % self.NumEvents)

    ## @brief Process a meta event.
    #
    #  This is relevant for lsf files only.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object.

    def processMetaEvent(self, meta):
	self.MetaEventProcessor.process(meta)

    ## @brief Global event processing sequence for lsf files.
    #
    #  @li reset the tree variables
    #  @li process the meta part of the event 
    #  @li process the event part of the event 
    #  @li fill the tree
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object.
    ## @param event
    #  The event object.
    
    def processLSF(self, meta, event):
	self.TreeMaker.resetVariables()
        self.processMetaEvent(meta)
        self.processEvent(event)
	self.TreeMaker.fillTree()

    ## @brief Start the event loop for lsf files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    
    def startLSFProcessing(self, maxEvents):
        while (self.NumEvents != maxEvents):
            try:
                (meta, buff) = self.LsfMerger.getUncompressedEvent()
            except TypeError:
                logging.info('End of file reached.')
                break
            self.processLSF(meta, buff)
        self.finalize()

    ## @brief Global event processing sequence for ldf files.
    #
    #  @li reset the tree variables
    #  @li process the event part of the event 
    #  @li fill the tree
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.

    def processLDF(self, event):
	self.TreeMaker.resetVariables()
        self.processEvent(event)
	self.TreeMaker.fillTree()

    ## @brief Start the event loop for ldf files.
    ## @param self
    #  The class instance.
    ## @param maxEvents
    #  The maximum number of events.
    
    def startLDFProcessing(self, maxEvents):
        while (self.NumEvents != maxEvents):
    	    event = self.LdfFile.read(8)
    	    if len(event) < 8:
    	      logging.info("End of File reached.")
              break
    	    else:
    	      (identity, length) = struct.unpack('!LL', event)
    	      event += self.LdfFile.read(length - 8)
	      self.processLDF(event)
        self.finalize()
     

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
    dataProcessor.start(options.events)
