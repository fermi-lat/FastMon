#! /bin/env python

## @package pRootTreeProcessor
## @brief Module responsible for processing the output ROOT tree and creating
#  all the requested plots.

import time
import ROOT
import logging
import sys
import pConfig

from pXmlParser    import pXmlParser
from pGlobals      import *
from pAlarmHandler import pAlarmHandler


## @brief Implementation of the ROOT tree processor.

class pRootTreeProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The xml parser containing the requested output lists.
    ## @param inputFilePath
    #  Path to the input ROOT file.
    ## @param outputFilePath
    #  Path to the output ROOT file.

    def __init__(self, xmlParser, inputFilePath, outputFilePath=None):

        ## @var __XmlParser
        ## @brief The xml parser containing the requested output lists.

        ## @var __InputRootFile
        ## @brief The input ROOT TFile object.

        ## @var __OutputFilePath
        ## @brief Path to the output ROOT file.

        ## @var __OutputRootFile
        ## @brief The output ROOT TFile object.

        ## @var __RootTree
        ## @brief The ROOT TTree object to be read from the input file.

        ## @var __AlarmHandler
        ## @brief The pAlarmHandler object implementing the automated controls
        #  on the ROOT plots.
        
        self.__XmlParser      = xmlParser
        self.__InputRootFile  = ROOT.TFile(inputFilePath)
        if outputFilePath is None:
            outputFilePath    = inputFilePath.replace('.root',\
                                                      '_processed.root')
        self.__OutputFilePath = outputFilePath
        self.__OutputRootFile = None
        self.__RootTree       = self.__getRootTree()
        self.__AlarmHandler   = pAlarmHandler()
        self.__setupAlarmHandler()

    ## @brief Dive into the input ROOT file and try and get the ROOT tree.
    ## @param self
    #  The class instance.
    
    def __getRootTree(self):
        rootTree = self.__InputRootFile.Get(ROOT_TREE_NAME)
        if rootTree is None:
            sys.exit('Could not find the %s ROOT tree in the input file %s.' %\
                     (ROOT_TREE_NAME, self.__InputRootFile.GetName()))
        else:
            return rootTree

    ## @brief Open the output ROOT file.
    ## @param self
    #  The class instance.

    def openOutputFile(self):
        self.__OutputRootFile = ROOT.TFile(self.__OutputFilePath, 'recreate')

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.

    def closeOutputFile(self):
        self.__OutputRootFile.Write()
        self.__OutputRootFile.Close()

    ## @brief Setup the alarm handler, based on the input configuration file.
    ## @param self
    #  The class instance.

    def __setupAlarmHandler(self):
        logging.info('Setting up the alarm handler...')
        startTime = time.time()
        for plotRep in self.__XmlParser.EnabledPlotRepsDict.values():
            plotRep.addAlarms(self.__AlarmHandler)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Setup the alarm handler.
    ## @param self
    #  The class instance.

    def __activateAlarmHandler(self):
        logging.info('Activating the alarm handler...')
        startTime = time.time()
        for plotRep in self.__XmlParser.EnabledPlotRepsDict.values():
            plotRep.activateAlarms(self.__AlarmHandler)
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Process the ROOT tree.
    ## @param self
    #  The class instance.

    def process(self):
        logging.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.openOutputFile()
        self.__createObjects()
        logging.info('Done in %s s.\n' % (time.time() - startTime))
        self.__activateAlarmHandler()
        print self.__AlarmHandler
        self.closeOutputFile()

    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def __createObjects(self):
        for rep in self.__XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.__RootTree)



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog [options] data_file')
    parser.add_option('-c', '--config-file', dest='config_file',\
                      default='../xml/config.xml', type=str,   \
                      help='path to the input xml configuration file')
    parser.add_option('-o', '--output-file', dest='output_file',
                      default=None, type=str,
                      help='path to the output ROOT file')
    (options, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('incorrect number of arguments')
        sys.exit()

    xmlParser = pXmlParser(options.config_file)
    processor = pRootTreeProcessor(xmlParser, args[0], options.output_file)
    processor.process()


    



