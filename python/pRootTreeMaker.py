import random
import numpy

from ROOT                        import TFile, TTree, TH1F
from pContributionIteratorWriter import *
from pContributionWriter         import *
from pRootTreeProcessor          import pRootTreeProcessor


class pRootTreeMaker:

    def __init__(self, xmlParser):
        self.__RootFile  = TFile('IsocDataFile.root', 'recreate')
        self.__RootTree  = TTree('IsocDataTree', 'IsocDataTree')
        self.__XmlParser = xmlParser
        self.__Processor = pRootTreeProcessor(self.__RootTree,\
                                              self.__XmlParser)
        self.DefaultVariablesDictionary = None
        self.VariablesDictionary = None        
        self.__updateIterators()
        self.__updateContributions()
        self.__createTree()

    def __updateIterators(self):
        writer = pTKRcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()
        writer = pCALcontributionIteratorWriter(self.__XmlParser)
        writer.writeIterator()

    def __updateContributions(self):
        writer = pGEMcontributionWriter(self.__XmlParser)
        writer.writeComponent()
   

    def __createTree(self):
        self.VariablesDictionary = {}
        self.__createDefaultBranches()
        for variable in self.__XmlParser.EnabledVariablesDict.values():
            self.VariablesDictionary[variable.getName()] = variable.Array
            self.__createTreeBranch(variable)

    def __createTreeBranch(self, variable):
        self.__RootTree.Branch(variable.getName(),\
                               self.VariablesDictionary[variable.getName()],\
                               variable.LeafList)

    def __createDefaultBranches(self):
        self.DefaultVariablesDictionary = {}
        variable_name = 'event_timestamp'
        variable = numpy.zeros(1, 'double')
        self.DefaultVariablesDictionary[variable_name] = variable
        self.__RootTree.Branch(variable_name, variable,\
                               '%s[1]/D' % variable_name)
        
    def fillTree(self):
        self.__RootTree.Fill()

    def resetVariables(self):
        for variable in self.__XmlParser.EnabledVariablesDict.values():
            variable.reset()

    def close(self):
        self.__Processor.process()
        self.__RootFile.Write()
        self.__RootFile.Close()

