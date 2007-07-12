
from pBaseTreeProcessor import pBaseTreeProcessor
from pFastMonTreeMaker  import FAST_MON_TREE_NAME


class pFastMonTreeProcessor(pBaseTreeProcessor):

    def __init__(self, dataProcessor):
        pBaseTreeProcessor.__init__(self, dataProcessor.XmlParser,\
                                    dataProcessor.OutputFilePath ,\
                                    FAST_MON_TREE_NAME, None)
    
