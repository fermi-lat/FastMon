
## @package pXmlParser
## @brief Basic xml configuration file parser.

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlParser')

import sys
import os
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
    ## @param configFilePath
    #  Path to the input xml configuration file.
    ## @param baseConfigFilePath
    #  Path to the base input xml configuration file (the one containing the
    #  input variables which should *not* be disabled).

    def __init__(self, configFilePath=None):

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

        startTime = time.time()
        self.InputListsDict       = {}
        self.EnabledVariablesDict = {} 
        self.OutputListsDict      = {}
        self.EnabledPlotRepsDict  = {}
        if XML_CONFIG_DIR_VAR_NAME in os.environ:
            xmlCfgDirPath = os.environ[XML_CONFIG_DIR_VAR_NAME]
            baseConfigFilePath = os.path.join(xmlCfgDirPath, 'baseConfig.xml')
            if configFilePath is None:
                configFilePath = os.path.join(xmlCfgDirPath, 'config.xml')
        else:
            sys.exit("Environmental variable %s not found. Exiting..."\
	    %  XML_CONFIG_DIR_VAR_NAME)
        filePathsList = [baseConfigFilePath, configFilePath]
        for filePath in filePathsList:
            logger.info('Parsing input xml file %s...' % filePath)
            if os.path.exists(filePath):
                self.XmlDoc = minidom.parse(file(filePath))
            else:
                sys.exit('Input configuration file %s not found. Exiting...' %\
                         filePath)
            self.populateInputLists()
            self.populateOutputLists()
            logger.info('Done in %.2f s.\n' % (time.time() - startTime))

    ## @brief Populate the input lists from the xml config file.
    ## @param self
    #  The class instance.

    def populateInputLists(self):
        logger.debug('Populating input lists...')
        for element in self.XmlDoc.getElementsByTagName('inputList'):
            list = pXmlInputList(element)
            self.InputListsDict[list.getName()] = list
            if list.Enabled:
                for (key, value) in list.EnabledVariablesDict.items():
                    self.EnabledVariablesDict[key] = value

    ## @brief Populate the output lists from the xml config file.
    ## @param self
    #  The class instance.

    def populateOutputLists(self):
        logger.debug('Populating output lists...')
        for element in self.XmlDoc.getElementsByTagName('outputList'):
            list = pXmlOutputList(element)
            self.OutputListsDict[list.getName()] = list
            if list.Enabled:
                for (key, value) in list.EnabledPlotRepsDict.items():
                    self.EnabledPlotRepsDict[key] = value

    ## @brief Cross check the input and output lists to make sure that all the
    #  variables which are necessary for the processing of the tree are
    #  correctly filled.
    ## @todo To be implemented.
    ## @param self
    #  The class instance.

    def crossCheckLists(self):
        pass

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
    
