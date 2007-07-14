
from pBaseTreeProcessor import pBaseTreeProcessor
from pFastMonTreeMaker  import FAST_MON_TREE_NAME


class pFastMonTreeProcessor(pBaseTreeProcessor):

    def __init__(self, dataProcessor):
        pBaseTreeProcessor.__init__(self, dataProcessor.XmlParser          ,\
                                    dataProcessor.TreeMaker.OutputFilePath ,\
                                    FAST_MON_TREE_NAME, None)
    
    ## @brief Create the ROOT objects defined in the enabled output lists
    #  of the xml configuration file.
    ## @param self
    #  The class instance.

    def createObjects(self):
        for rep in self.XmlParser.EnabledPlotRepsDict.values():
            rep.createRootObjects(self.RootTree)
