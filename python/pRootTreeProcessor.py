## @package pRootTreeProcessor
## @brief Module responsible for processing the output ROOT tree and creating
#  all the requested plots.

import time
import ROOT
import logging

from pXmlParser import pXmlParser


## @brief Implementation of the ROOT tree processor.

class pRootTreeProcessor:

    ## @brief Constructor.
    ## @param self
    #  The class instance.
    ## @param rootTree
    #  The input ROOT tree.
    ## @param xmlParser
    #  The xml parser containing the requested output lists.

    def __init__(self, rootTree, xmlParser):

        ## @var __XmlParser
        ## @brief The xml parser containing the requested output lists.

        ## @var __RootTree
        ## @brief The input ROOT tree.
        
        self.__XmlParser = xmlParser
        self.__RootTree  = rootTree

    ## @brief Process the ROOT tree.
    ## @param self
    #  The class instance.

    def process(self):
        logging.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.__createObjects()
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def __createObjects(self):
        for rep in self.__XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.__RootTree)


if __name__ == '__main__':
    f = ROOT.TFile('IsocDataFile.root')
    tree = f.Get('IsocDataTree')
    parser = pXmlParser('config.xml')
    processor = pRootTreeProcessor(tree, parser)
    outputFile = ROOT.TFile('data/output.root', 'recreate')
    processor.process()       
    processor.stripchart()
    outputFile.Write()
    outputFile.Close()
