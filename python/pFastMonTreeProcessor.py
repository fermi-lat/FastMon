#! /bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pFastMonTreeProcessor')

from pBaseTreeProcessor import pBaseTreeProcessor
from pFastMonTreeMaker  import FAST_MON_TREE_NAME
from pCustomPlotter     import pCustomPlotter

import time


class pFastMonTreeProcessor(pBaseTreeProcessor):

    def __init__(self, xmlParser, inputFilePath):
        pBaseTreeProcessor.__init__(self, xmlParser, inputFilePath,\
                                    FAST_MON_TREE_NAME, None)

    def run(self):
        logger.info('Processing the root tree and writing histograms...')
        startTime = time.time()
        self.open()
        self.CustomPlotter = pCustomPlotter(self.OutputFilePath, self.RootTree)
        self.createObjects()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.CustomPlotter.cleanup()
        self.close()
    
    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def createObjects(self):
        for rep in self.XmlParser.EnabledPlotRepsDict.values():
            if rep.__class__.__name__ == 'pCUSTOMXmlRep':
                rep.setPlotter(self.CustomPlotter)
            rep.createRootObjects(self.RootTree)


if __name__ == '__main__':
    from pXmlParser import pXmlParser
    from pOptionParser import pOptionParser
    optparser = pOptionParser('crvL',1,1,False)

    xmlParser = pXmlParser(optparser.Options.c)
    treeProcessor = pFastMonTreeProcessor(xmlParser, optparser.Argument)
    treeProcessor.run()
##     if optparser.Options.r:
##         from pFastMonReportGenerator  import pFastMonReportGenerator
##         ReportGenerator = pFastMonReportGenerator(self)
##         ReportGenerator.run(optparser.Options.v,\
##                                           not optparser.Options.L)
