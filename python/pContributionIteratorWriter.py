
import time
import logging

from pCodeGenerator         import pCodeGenerator


class pContributionIteratorWriter(pCodeGenerator):

    __CONSTRUCTOR_PARAMETERS = '(self, event, contribution, treeMaker)'

    def __init__(self, className):
        pCodeGenerator.__init__(self)
        self.ClassName     = className
        self.BaseClassName = '%sBase' % self.ClassName 
        self.FileName      = '%s.py'  % self.ClassName
        self.openFile(self.FileName)

    def writeIterator(self):
        logging.info('Writing %s...' % self.FileName)
        startTime = time.time()
        self.writeImportStatement(self.BaseClassName, '*')
        self.writeClassDefinition(self.ClassName, self.BaseClassName)
        self.writeConstructorDefinition(self.__CONSTRUCTOR_PARAMETERS)
        self.writeLine('%s.__init__%s' % (self.BaseClassName,\
                                          self.__CONSTRUCTOR_PARAMETERS))
        self.backup()
        self.writeMethodDefinition('fillEventContribution')
        self.implementIterator()
        self.backup()
        logging.info('Done in %s s.\n' % (time.time() - startTime))

    def implementIterator(self):
        self.writeLine('pass')


class pTKRcontributionIteratorWriter(pContributionIteratorWriter):

    __CLASS_NAME       = 'pTKRcontributionIterator'
    __STRIP_PARAMETERS = '(self, tower, layerEnd, hit)'
    __TOT_PARAMETERS   = '(self, tower, layerEnd, tot)'

    def __init__(self, xmlParser):
        pContributionIteratorWriter.__init__(self, self.__CLASS_NAME)
        self.__Variables = xmlParser.getEnabledVariablesByGroup('TKR')
        baseClassName = '%sBase'            % (self.__CLASS_NAME)
        exec('from %s import %s'            % (baseClassName, baseClassName))
        exec('self.BaseFunctions = dir(%s)' % (baseClassName))

    def implementIterator(self):
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if variable.getName() == function:
                        self.writeLine('self.%s()' % function)
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')
        self.__implementStrip()
        self.__implementTOT()

    def __implementStrip(self):
        self.backup()
        self.writeMethodDefinition('strip', self.__STRIP_PARAMETERS)
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if ('%s__strip__' % variable.getName()) == function:
                        self.writeLine('self.%s%s' %\
                                       (function, self.__STRIP_PARAMETERS.replace('self, ', '')))
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')

    def __implementTOT(self):
        self.backup()
        self.writeMethodDefinition('TOT', self.__TOT_PARAMETERS)
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if ('%s__TOT__' % variable.getName()) == function:
                        self.writeLine('self.%s%s' %\
                                       (function, self.__TOT_PARAMETERS.replace('self, ', '')))
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')


class pCALcontributionIteratorWriter(pContributionIteratorWriter):

    __CLASS_NAME       = 'pCALcontributionIterator'
    __LOG_PARAMETERS   = '(self, tower, layer, calLog)'

    def __init__(self, xmlParser):
        pContributionIteratorWriter.__init__(self, self.__CLASS_NAME)
        self.__Variables  = xmlParser.getEnabledVariablesByGroup('CAL')
        baseClassName = '%sBase'            % (self.__CLASS_NAME)
        exec('from %s import %s'            % (baseClassName, baseClassName))
        exec('self.BaseFunctions = dir(%s)' % (baseClassName))

    def implementIterator(self):
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if variable.getName() == function:
                        self.writeLine('self.%s()' % function)
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')
        self.__implementLog()

    def __implementLog(self, implementation='pass'):
        self.backup()
        self.writeMethodDefinition('log', self.__LOG_PARAMETERS)
        somethingDone = False
        if len(self.__Variables):
            for variable in self.__Variables:
                for function in self.BaseFunctions:
                    if ('%s__log__' % variable.getName()) == function:
                        self.writeLine('self.%s%s' %\
                                       (function, self.__LOG_PARAMETERS.replace('self, ', '')))
                        somethingDone = True
        if not somethingDone:
            self.writeLine('pass')


if __name__ == '__main__':
    from pXmlParser import pXmlParser
    parser = pXmlParser('config.xml')
    w = pTKRcontributionIteratorWriter(parser)
    w.writeIterator()
    w = pCALcontributionIteratorWriter(parser)
    w.writeIterator()
