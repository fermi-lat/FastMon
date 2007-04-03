## @package pContributionWriter
## @brief Package responsible for dinamically writing the required event
#  contributions.

import time
import logging

from pCodeGenerator         import pCodeGenerator


## @brief Base class for the contribution writer.

class pContributionWriter(pCodeGenerator):

    ## @var __CONSTRUCTOR_PARAMETERS
    ## @brief Base constructor parameters.
    
    __CONSTRUCTOR_PARAMETERS = '(self, event, contribution, treeMaker)'

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param className
    #  The contribution class name.
    
    def __init__(self, className):

        ## @var ClassName
        ## @brief The contribution class name.

        ## @var BaseClassName
        ## @brief The name of the base class from which the contribution class 
        #  inherits.
        #
        #  It is the class name itself with a "Base" postpended.

        ## @var FileName
        ## @brief The file name in which the class declaration is written.
        #
        #  It is the class name with a ".py" postpended.
        
        pCodeGenerator.__init__(self)
        self.ClassName     = className
        self.BaseClassName = '%sBase' % self.ClassName 
        self.FileName      = '%s.py'  % self.ClassName
        self.openFile(self.FileName)

    ## @brief Write the actual component to file.
    ## @param self
    #  The class instance.    

    def writeComponent(self):
        logging.info('Writing %s...' % self.FileName)
        startTime = time.time()
        self.writeImportStatement(self.BaseClassName, '*')
        self.writeClassDefinition(self.ClassName, self.BaseClassName)
        self.writeConstructorDefinition(self.__CONSTRUCTOR_PARAMETERS)
        self.writeLine('%s.__init__%s' % (self.BaseClassName,\
                                          self.__CONSTRUCTOR_PARAMETERS))
        self.backup()
        self.writeMethodDefinition('fillEventContribution')
        self.implementComponent()
        self.backup()
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    ## @brief Implement the component according to the xml configuration
    #  file.
    #
    #  This is actually implemented in the sub-classes.
    ## @param self
    #  The class instance.     

    def implementComponent(self):
        pass


## @brief Implementation of the contribution writer for the GEM.

class pGEMcontributionWriter(pContributionWriter):

    ## @var __CLASS_NAME
    ## @brief The GEM contribution class name.

    __CLASS_NAME       = 'pGEMcontribution'

    ## @brief Constructor
    ## @param self
    #  The class instance.
    ## @param xmlParser
    #  The pXmlParser object containing the definition of the relevant
    #  variabled.

    def __init__(self, xmlParser):

        ## @var __Variables
        ## @brief List of the GEM enabled variables, as passed by the
        #  xml parser.
        
        pContributionWriter.__init__(self, self.__CLASS_NAME)
        self.__Variables = xmlParser.getEnabledVariablesByGroup('GEM')
        baseClassName    = '%sBase'         % (self.__CLASS_NAME)
        exec('from %s import %s'            % (baseClassName, baseClassName))
        exec('self.BaseFunctions = dir(%s)' % (baseClassName))

    ## @brief Implement the component according to the xml configuration
    #  file.
    ## @param self
    #  The class instance.

    def implementComponent(self):
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if variable.getName() == function:
                        self.writeLine('self.%s()' % function)
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')



if __name__ == '__main__':
    from pXmlParser import pXmlParser
    parser = pXmlParser('config.xml')
    w = pGEMcontributionWriter(parser)
    w.writeComponent()
