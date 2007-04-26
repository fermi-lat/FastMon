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
import pConfig

from copy 			      import copy
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
from pErrorHandler                    import pErrorHandler
from pAlarmHandler                    import pAlarmHandler
from pRootTreeProcessor               import pRootTreeProcessor
from pTestReportGenerator             import pTestReportGenerator


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
    ## @param processTree
    #  Flag to launch the pRootTree processor after the tree has been created.
    ## @param generateReport
    #  Flag to generate a report at the end of the analysis.
    ## @param reportDirPath
    #  The report output directory.
    ## @param forceOverwrite
    #  Flag to overwrite existing files without asking the user.
    ## @param verbose
    #  Print additional informations.

    def __init__(self, inputFilePath, configFilePath=None, outputDir=None, outputFileName=None,\
                 processTree=False, generateReport=False,\
                 forceOverwrite=False, verbose=False):

        ## @var __ProcessTree
        ## @brief Flag to launch the pRootTree processor after the tree
        #  has been created.

        ## @var __GenerateReport
        ## @brief Flag to run the report generation at the end of the
        #  analysis.

        ## @var __ReportDirPath
        ## @brief The path to the output report directory.

        ## @var __ForceOverwrite
        ## @brief Flag to overwrite existing files without asking the user.

        ## @var __Verbose
        ## @brief Print additional informations.

        ## @var __XmlParser
        ## @brief The xml parser object (pXmlParser instance).

        ## @var __OutputFilePath
        ## @brief The path to the output ROOT file containing the ROOT tree.
        #
        #  Not that this is the input file for the tree processor, if the
        #  data processor is called with the corresponding option.

        ## @var __ErrorsFilePath
        ## @brief The path to the output file where the errors summary is
        #  saved.

        ## @var __TreeMaker
        ## @brief The tree maker object (pRootTreeMaker instance).

        ## @var __ErrorCounter
        ## @brief The error counter object (pEventErrorCounter instance).

        ## @var __MetaEventProcessor
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

        if outputDir is None:
            outputDir = os.path.split(inputFilePath)[0]
            
        fileName = os.path.split(inputFilePath)[1]
        outputDir = os.path.join(outputDir,fileName.split('.')[0] )
        
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
        
        if outputFileName is None:
            outputFileName    = '%s.root' % fileName.split('.')[0]
                        
        self.__OutputFilePath = os.path.join(outputDir, outputFileName)

        
        self.__ProcessTree    = processTree
        self.__GenerateReport = generateReport
        self.__ForceOverwrite = forceOverwrite
        self.__Verbose        = verbose
        self.__XmlParser      = pXmlParser(configFilePath)
        
        self.__ErrorsFilePath =\
                              self.__OutputFilePath.replace('.root', '.errors')
        self.__TreeMaker      = pRootTreeMaker(self.__XmlParser,\
                                               self.__OutputFilePath)

        self.__ErrorCounter   = pErrorHandler()
	self.__MetaEventProcessor = pMetaEventProcessor(self.__TreeMaker)
        self.__updateContributionIterators()
        self.__updateContributions()
        from pLATcomponentIterator    import pLATcomponentIterator
        self.LatCompIter      = pLATcomponentIterator(self.__TreeMaker,\
                                                      self.__ErrorCounter)
        self.EbfEventIter     = pEBFeventIterator(self.LatCompIter)
        self.LatContrIter     = pLATcontributionIterator(self.EbfEventIter)
        self.LatDatagrIter    = pLATdatagramIterator(self.LatContrIter)
        self.LatDataBufIter   = LDF.LATdataBufferIterator(self.LatDatagrIter)
        self.NumEvents        = None
        self.LsfMerger        = None
        self.LdfFile          = None
        self.StartTime        = None
        self.StopTime         = None
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
            logging.info('Done.\n')
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
        self.__TreeMaker.closeFile()
        print
        logging.info('Done. %d events processed in %s s (%f Hz).\n' %\
                     (self.NumEvents, elapsedTime, averageRate))
        self.__ErrorCounter.writeDoxygenSummary(self.__ErrorsFilePath)
        self.__ErrorCounter.dump('%s.pickle' % self.__ErrorsFilePath)
        print self.__ErrorCounter
        if self.__ProcessTree:
            self.processTree()
            

    ## @brief Process the ROOT tree.
    #
    #  This function creates a pRootTreeProcessor object which re-opens
    #  the data processor output files and produces a second ROOT file
    #  containing the histogram defined in the xml configuration file.
    ## @param self
    #  The class instance.
        
    def processTree(self):
        treeProcessor = pRootTreeProcessor(self.__XmlParser,\
                                           self.__OutputFilePath,
                                           None,
                                           self.__GenerateReport,
                                           None,
                                           None,
                                           self.__ForceOverwrite,
                                           self.__Verbose)
        treeProcessor.process()

    ## @brief Process an event.
    #
    #  This is actually called both for lsf and ldf files.
    ## @param self
    #  The class instance.
    ## @param event
    #  The event object.
 
    def processEvent(self, event):
        self.__ErrorCounter.setEventNumber(self.NumEvents)
	self.LatDataBufIter.iterate(event, len(event))
        label = 'processor_event_number'
        self.__TreeMaker.VariablesDictionary[label][0] = self.NumEvents
        self.NumEvents += 1
        if not self.NumEvents % 100:
            print '\r%s events processed...' % self.NumEvents,
            sys.stdout.flush()

    ## @brief Process a meta event.
    #
    #  This is relevant for lsf files only.
    ## @param self
    #  The class instance.
    ## @param meta
    #  The meta-event object.

    def processMetaEvent(self, meta):
	self.__MetaEventProcessor.process(meta)

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
	self.__TreeMaker.resetVariables()
        self.processMetaEvent(meta)
        self.processEvent(event)
	self.__TreeMaker.fillTree()

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
	self.__TreeMaker.resetVariables()
        self.processEvent(event)
	self.__TreeMaker.fillTree()

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
    parser.add_option('-c', '--config-file', dest='config_file',
                      default=None, type=str,
                      help='path to the input xml configuration file')
    parser.add_option('-n', '--num-events', dest='events',
                      default=-1, type=int,
                      help='number of events to be processed')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='name of the output ROOT file')
    parser.add_option('-d', '--output-dir', dest='output_dir',
                      default=None, type=str,
                      help='path to the output directory')
    parser.add_option('-p', '--process-tree', action='store_true',
                      dest='process_tree', default=False,
                      help='process the ROOT tree and create histograms')
    parser.add_option('-r', '--create-report', action='store_true',
                      dest='create_report', default=False,
                      help='generate the report from the processed ROOT file')
    parser.add_option('-f', '--force-overwrite', action='store_true',
                      dest='force_overwrite', default=False,
                      help='overwrite existing files without asking')
    parser.add_option('-v', '--verbose', action='store_true',
                      dest='verbose', default=False,
                      help='print a lot of ROOT/doxygen/LaTeX related stuff')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()
    if options.create_report and not options.process_tree:
        parser.print_help()
        parser.error('please run with the -p option if you want the report.')
    
    dataProcessor  = pDataProcessor( args[0],options.config_file, options.output_dir,
                                    options.output_file, options.process_tree,
                                    options.create_report,
                                    options.force_overwrite, options.verbose)
    dataProcessor.start(options.events)
