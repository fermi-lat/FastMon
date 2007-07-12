
import pSafeLogger
logger = pSafeLogger.getLogger('pFastMonTreeMaker')

from pBaseTreeMaker import pBaseTreeMaker


FAST_MON_TREE_NAME = 'IsocDataTree'

class pFastMonTreeMaker(pBaseTreeMaker):

    def __init__(self, dataProcessor):
        pBaseTreeMaker.__init__(self, dataProcessor.XmlParser,\
                                dataProcessor.OutputFilePath ,\
                                FAST_MON_TREE_NAME)
