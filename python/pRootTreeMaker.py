## @package pRootTreeMaker
## @brief Package responsible for the creation of the output ROOT tree,
#  based on the xml configuration file.

import random
import numpy
import logging

from ROOT                        import TFile, TTree, TH1F
from pRootTreeProcessor          import pRootTreeProcessor
from pXmlParser                  import pXmlParser


## @brief Implementation of the ROOT tree maker.

class pRootTreeMaker:

    ## @brief Contructor.
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The pXmlParser object responsible for reading the configuration file.
    ## @param outputFilePath
    #  The path to the output ROOT file.

    def __init__(self, xmlParser, outputFilePath):

        ## @var __RootFile
        ## @brief The output ROOT TFile object.

        ## @var __RootTree
        ## @brief The output ROOT TTree object.

        ## @var __XmlParser
        ## @brief The pXmlParser object responsible for the parsing of the
        #  configuration file.

        ## @var VariablesDictionary
        ## @brief The dictionary containing the tree variables
        #  (which are numpy.array objects).
 
        self.__RootFile  = TFile(outputFilePath, 'recreate')
        self.__RootTree  = TTree('IsocDataTree', 'IsocDataTree')
        self.__XmlParser = xmlParser
        self.VariablesDictionary = {}
        self.__createBranches()
        logging.info('Created File %s with Tree %s\n' %\
                     (outputFilePath, self.__RootTree.GetName()) )

    ## @brief Return the ROOT tree.
    ## @param self
    #  The class instance.   

    def getRootTree(self):
        return self.__RootTree

    ## @brief Create all the tree branches, based on the information
    #  from the xml parser.
    ## @param self
    #  The class instance.

    def __createBranches(self):
        for variable in self.__XmlParser.EnabledVariablesDict.values():
            self.VariablesDictionary[variable.getName()] = variable.Array
            self.__createTreeBranch(variable)

    ## @brief Create the tree branch for a specific variable.
    ## @param self
    #  The class instance.
    ## @param variable
    #  The xml variable representation from the pXmlParser object.

    def __createTreeBranch(self, variable):
        self.__RootTree.Branch(variable.getName(),\
                               self.VariablesDictionary[variable.getName()],\
                               variable.LeafList)

    ## @brief Fill the ROOT tree.
    ## @param self
    #  The class instance.

    def fillTree(self):
        self.__RootTree.Fill()

    ## @brief Return a specific variable from VariablesDictionary.
    ## @param self
    #  The class instance.
    ## @param name
    #  The VariablesDictionary key corresponding to the desired variable. 

    def getVariable(self, name):
        return self.VariablesDictionary[name]

    ## @brief Reset variable Array
    ## @param self
    #  The class instance.

    def resetVariables(self):
        for variable in self.__XmlParser.EnabledVariablesDict.values():
            variable.reset()	    

    ## @brief Close the output ROOT file.
    ## @param self
    #  The class instance.
    
    def closeFile(self):
        self.__RootFile.Write()
        self.__RootFile.Close()

