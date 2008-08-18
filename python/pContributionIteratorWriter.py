
## @package pContributionIteratorWriter
## @brief Package for automated implementation of event iterators, based
#  on a xml input file.

import pSafeLogger
logger = pSafeLogger.getLogger('pContributionIteratorWriter')

import time

from pCodeGenerator         import pCodeGenerator


CONSTRUCTOR_PARAMETERS = '(self, event, contribution, treeMaker, errorCounter)'

## @brief Base class implementing the iterator writers.
#
#  Subclassed for all the subsystems (TKR, CAL, ACD, etc).
#  The scheme here is the following: base classes for all the iterators exist,
#  with functions defined for all the possible variables (e.g. the TKR
#  subsystem has its pTKRcontributionIteratorBase class defined in
#  pTKRcontributionIteratorBase.py). This class creates a new python file
#  (in the TKR case it will be called pTKRcontributionIterator.py) defining
#  a subclass (e.g. pTKRcontributionIterator) in which *only* the functions
#  corresponding to the variables in the xml input list are called.

class pContributionIteratorWriter(pCodeGenerator):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  Reference to the pXmlParser object responsible for the variables list.
    ## @param className
    #  The iterator class name.
    ## @param groupName
    #  The group name identifying the relevant variables in the input list.

    def __init__(self, xmlParser, className, groupName):

        ## @var ClassName
        ## @brief The name of the class implementing the actual iterator
        #  (need to match the base iterator class).

        ## @var BaseClassName
        ## @brief The name of the base class (statically defined:
        #  pTKRcontributionIteratorBase for the TKR etc).

        ## @var FileName
        ## @brief The name of the file in which the iterator is defined.

        ## @var Variables
        ## @brief The variables which need to be filled by the iterator, as
        #  defined in the corresponding input lists group of the the xml
        #  configuration file.

        ## @var Parameters
        ## @brief Dictionary of parameters for the specific subsystem
        #  iterator functions (i.e. strip() and TOT() for the TKR, log() for
        #  the CAL etc).
        
        pCodeGenerator.__init__(self)
        self.ClassName     = className
        self.BaseClassName = '%sBase' % self.ClassName 
        self.FileName      = '%s.py'  % self.ClassName
        self.openFile(self.FileName)
        self.Variables     = xmlParser.getEnabledVariablesByGroup(groupName)
        exec('from %s import %s'            % (self.BaseClassName,\
                                               self.BaseClassName))
        exec('self.BaseFunctions = dir(%s)' % (self.BaseClassName))
        self.Parameters    = {}

    ## @brief Write the iterator class to file.
    #
    #  Implements both the fillEventContribution() method and the
    #  subsystem-specific functions.
    ## @param self
    #  The class instance.

    def writeIterator(self):
        logger.info('Writing %s...' % self.FileName)
        startTime = time.time()
        self.writeImportStatement(self.BaseClassName, '*')
        self.writeClassDefinition(self.ClassName, self.BaseClassName)
        self.writeConstructorDefinition(CONSTRUCTOR_PARAMETERS)
        self.writeLine('%s.__init__%s' % (self.BaseClassName,\
                                          CONSTRUCTOR_PARAMETERS))
        self.backup()
        self.implementIterator()
        self.implementFunctions()
        self.backup()
        logger.info('Done in %.4f s.\n' % (time.time() - startTime))

    ## @brief Write to file the implementation of the fillEventContribution()
    #  method of the iterator (which is the main function, called whenever
    #  the iterator itself is called).
    ## @param self
    #  The class instance.

    def implementIterator(self):
        self.writeMethodDefinition('fillEventContribution')
        somethingDone = False
        if len(self.Variables):
            for variable in self.Variables:
                for function in self.BaseFunctions:
                    if variable.getName() == function:
                        self.writeLine('self.%s()' % function)
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')

    ## @brief Implement a subsystem-specific function (e.g. strip() for
    #  the TKR), based on the function name.
    ## @param self
    #  The class instance.
    ## @param functionName
    #  The name of the function.

    def implementFunction(self, functionName):
        parameters = self.Parameters[functionName]
        self.backup()
        self.writeMethodDefinition(functionName, parameters)
        self.writeLine('%s.%s%s' % (self.BaseClassName, functionName,\
                                    parameters))
        if len(self.Variables):
            for variable in self.Variables:
                for function in self.BaseFunctions:
                    if ('%s__%s__' % (variable.getName(), functionName)) ==\
                           function:
                        self.writeLine('self.%s%s' %\
                                       (function,\
                                        parameters.replace('self, ', '')))

    ## @brief Implement all the subsystem-specific functions of the iterator,
    #  based on the key of the @ref Parameters variable.

    def implementFunctions(self):
        for functionName in self.Parameters.keys():
            self.implementFunction(functionName)
        

## @brief TKR iterator writer implementation. 

class pTKRcontributionIteratorWriter(pContributionIteratorWriter):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  Reference to the pXmlParser object responsible for the variables list.

    def __init__(self, xmlParser):

        ## @var Parameters
        ## @brief Dictionary of parameters for the TKR specific
        #  iterator functions: strip() and TOT().
        
        pContributionIteratorWriter.__init__(self, xmlParser,\
                                             'pTKRcontributionIterator', 'TKR')
        self.Parameters = {'strip': '(self, tower, layerEnd, hit)',
                           'TOT'  : '(self, tower, layerEnd, tot)'
                           }


## @brief CAL iterator writer implementation. 

class pCALcontributionIteratorWriter(pContributionIteratorWriter):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  Reference to the pXmlParser object responsible for the variables list.

    def __init__(self, xmlParser):

        ## @var Parameters
        ## @brief Dictionary of parameters for the CAL specific
        #  iterator functions: log().
        
        pContributionIteratorWriter.__init__(self, xmlParser,\
                                             'pCALcontributionIterator', 'CAL')
        self.Parameters = {'log': '(self, tower, layer, calLog)'
                           }


## @brief ACD iterator writer implementation. 

class pAEMcontributionIteratorWriter(pContributionIteratorWriter):

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  Reference to the pXmlParser object responsible for the variables list.

    def __init__(self, xmlParser):

        ## @var Parameters
        ## @brief Dictionary of parameters for the ACD specific
        #  iterator functions: header() and pha().
        
        pContributionIteratorWriter.__init__(self, xmlParser,\
                                             'pAEMcontributionIterator', 'ACD')
        self.Parameters = {'header': '(self, cable, header)',
                           'pha'   : '(self, cable, channel, pha)'
                           }


if __name__ == '__main__':
    from pXmlParser import pXmlParser
    parser = pXmlParser('../xml/config.xml')
    w = pTKRcontributionIteratorWriter(parser)
    w.writeIterator()
    w = pCALcontributionIteratorWriter(parser)
    w.writeIterator()
    w = pAEMcontributionIteratorWriter(parser)
    w.writeIterator()
