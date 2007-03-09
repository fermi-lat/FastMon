
import time
import logging

from pCodeGenerator         import pCodeGenerator


class pContributionWriter(pCodeGenerator):

    __CONSTRUCTOR_PARAMETERS = '(self, event, contribution, treeMaker)'
    
    def __init__(self, className):
        pCodeGenerator.__init__(self)
        self.ClassName     = className
        self.BaseClassName = '%sBase' % self.ClassName 
        self.FileName      = '%s.py'  % self.ClassName
        self.openFile(self.FileName)

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

    def implementComponent(self):
        pass


class pGEMcontributionWriter(pContributionWriter):

    __CLASS_NAME       = 'pGEMcontribution'

    def __init__(self, xmlParser):
        pContributionWriter.__init__(self, self.__CLASS_NAME)
        self.__Variables = xmlParser.getEnabledVariablesByGroup('GEM')
        baseClassName = '%sBase'            % (self.__CLASS_NAME)
        exec('from %s import %s'            % (baseClassName, baseClassName))
        exec('self.BaseFunctions = dir(%s)' % (baseClassName))

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
