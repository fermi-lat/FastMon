
## @package pXmlParser
## @brief Basic xml configuration file parser.

import sys
import os
import logging
import time

from xml.dom  import minidom
from pGlobals import *
from pXmlInputList  import pXmlInputList
from pXmlOutputList import pXmlOutputList


## @brief Class describing the xml parser.

class pXmlParser:

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param filePath
    #  Path to the input xml configuration file.

    def __init__(self, configFilePath):

        ## @var InputListsDict
        ## @brief Dictionary containing the input lists.

        ## @var EnabledVariablesDict
        ## @brief Dictionary containing the enabled input variables
        #  (including all the enabled input lists).

        ## @var OutputListsDict
        ## @brief Dictionary containing the output lists.

        ## @var EnabledPlotRepsDict
        ## @brief Dictionary containing the enabled output plot representations
        #  (including all the enabled output lists).

        ## @var XmlDoc
        ## @brief Representation of the xml configuration file from the
        #  xml.dom.minidom module.
        
        logging.info('Parsing input xml file...')
        if os.path.exists(configFilePath):
            self.XmlDoc           = minidom.parse(file(configFilePath))
        else:
            sys.exit('Input configuration file not found. Exiting...')
        startTime                 = time.time()
        self.InputListsDict       = {}
        self.EnabledVariablesDict = {} 
        self.OutputListsDict      = {}
        self.EnabledPlotRepsDict  = {}
        for element in self.XmlDoc.getElementsByTagName('inputList'):
            list = pXmlInputList(element)
            self.InputListsDict[list.getName()] = list
            if list.Enabled:
                for (key, value) in list.EnabledVariablesDict.items():
                    self.EnabledVariablesDict[key] = value
        for element in self.XmlDoc.getElementsByTagName('outputList'):
            list = pXmlOutputList(element)
            self.OutputListsDict[list.getName()] = list
            if list.Enabled:
                for (key, value) in list.EnabledPlotRepsDict.items():
                    self.EnabledPlotRepsDict[key] = value
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Return the number of input lists.
    ## @param self
    #  The class instance.

    def getNumInputLists(self):
        return len(self.InputListsDict)

    ## @brief Return the number of output lists.
    ## @param self
    #  The class instance.

    def getNumOutputLists(self):
        return len(self.OutputListsDict)

    ## @brief Return a list of all the enabled variables included
    #  in the enabled input lists corresponding to a given group.
    #
    #  This is useful when writing the iterators (where all the variables
    #  from a given group go into the iterator corresponding to that group).
    ## @param self
    #  The class instance.
    ## @param groupName
    #  The name of the group.

    def getEnabledVariablesByGroup(self, groupName):
        variablesList = []
        for list in self.InputListsDict.values():
            if list.Enabled and list.Group == groupName:
                variablesList += list.EnabledVariablesDict.values()
        return variablesList

    ## @brief Class representation.
    ## @param self
    #  The class instance.

    def __str__(self):
        return 'Num. input lists : %d\n' % self.getNumInputLists()          +\
               'Enabled variables: %s\n' % self.EnabledVariablesDict.keys() +\
               'Num. output lists: %d\n' % self.getNumOutputLists()         +\
               'Enabled plot reps: %s\n' % self.EnabledPlotRepsDict.keys()


if __name__ == '__main__':
    parser = pXmlParser('config.xml')
    print parser
