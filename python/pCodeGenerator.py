
import os
import logging
import time

class pCodeGenerator:

    __INDENTATION_SPACES = 4

    def __init__(self):
        self.__File             = None
        self.__IndentationLevel = None 

    def setIndentationLevel(self, level):
        self.__IndentationLevel = 0

    def indent(self):
        self.__IndentationLevel += 1

    def backup(self):
        if self.__IndentationLevel > 0:
            self.__IndentationLevel -= 1

    def openFile(self, filePath):
        self.__File = file(filePath, 'w')
        self.setIndentationLevel(0)
        self.writeLine('# Written by pCodeGenerator on %s' % time.asctime())
        self.writeLine('# Any change to this file will be lost.')
        self.skipLine()

    def skipLine(self):
        self.__File.writelines('\n')

    def skipLines(self, numLines):
        for i in range(numLines):
            self.skipLine()

    def writeLine(self, line):
        for i in range(self.__IndentationLevel):
            self.__File.writelines(self.__INDENTATION_SPACES*' ')
        self.__File.writelines('%s\n' % line)

    def writeImportStatement(self, module, object=None):
        if object is not None:
            line = 'from %s import %s' % (module, object)
        else:
            line = 'import %s' % module
        self.writeLine(line)
        self.skipLine()

    def writeClassDefinition(self, className, baseClassName=None):
        self.skipLine()
        if baseClassName is not None:
            line = 'class %s(%s):' % (className, baseClassName)
        else:
            line = 'class %s:' % className
        self.writeLine(line)
        self.skipLine()
        self.indent()

    def writeMethodDefinition(self, methodName, parameters='(self)'):
        self.skipLine()
        line = 'def %s%s:' % (methodName, parameters)
        self.writeLine(line)
        self.indent()

    def writeConstructorDefinition(self, parameters='(self)'):
        self.writeMethodDefinition('__init__', parameters)

    def closeFile(self):
        self.__File.close()
    


if __name__ == '__main__':
    g = pCodeGenerator()
    g.openFile('test.py')
    g.writeClassDefinition('A', 'B')
    g.writeConstructorDefinition()
    g.writeLine('pass')
    g.backup()
    g.skipLine()
    g.writeMethodDefinition('test', '(self, value)')
    g.writeLine('a = value')
    g.closeFile()
