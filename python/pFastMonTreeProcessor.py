
import pSafeLogger
logger = pSafeLogger.getLogger('pFastMonTreeProcessor')

from pBaseTreeProcessor import pBaseTreeProcessor
from pFastMonTreeMaker  import FAST_MON_TREE_NAME
from pCustomPlotter     import pCustomPlotter

import time


class pFastMonTreeProcessor(pBaseTreeProcessor):

    def __init__(self, dataProcessor):
        pBaseTreeProcessor.__init__(self, dataProcessor.XmlParser          ,\
                                    dataProcessor.TreeMaker.OutputFilePath,\
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
