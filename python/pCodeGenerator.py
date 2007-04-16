## @package pCodeGenerator
## @brief Module containing useful functions for dinamically writing python
#  code (used in iterator writers and contribution writers).

import os
import logging
import time
from pGlobals import *

## @brief Implementation of the code generator.

class pCodeGenerator:

    ## @var __INDENTATION_SPACES
    ## @brief The default number of spaces for the indentation.
    
    __INDENTATION_SPACES = 4

    ## @brief Constructor.
    ## @param self
    #  The class instance.

    def __init__(self):

        ## @var __File
        ## @brief The ouptut file to be created.

        ## @var __IndentationLevel
        ## @brief The current indentation level.
        
        self.__File             = None
        self.__IndentationLevel = None 

    ## @brief Set the indentation level.
    ## @param self
    #  The class instance.
    ## @param level
    #  The target indentation level.
    
    def setIndentationLevel(self, level):
        self.__IndentationLevel = level

    ## @brief Increase the indentation level by one unit.
    ## @param self
    #  The class instance.
    
    def indent(self):
        self.__IndentationLevel += 1

    ## @brief Decrease the indentation level by one unit.
    ## @param self
    #  The class instance.

    def backup(self):
        if self.__IndentationLevel > 0:
            self.__IndentationLevel -= 1

    ## @brief Open the output file.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The path to the file to be created.

    def openFile(self, filePath):
        if FASTMON_DIR_VAR_NAME in os.environ:
            filePath = os.path.join(os.environ[FASTMON_DIR_VAR_NAME], filePath)
        self.__File = file(filePath, 'w')
        self.setIndentationLevel(0)
        self.writeLine('# Written by pCodeGenerator on %s' % time.asctime())
        self.writeLine('# Any change to this file will be lost.')
        self.skipLine()

    ## @brief Write a carriage return to the output file.
    ## @param self
    #  The class instance.

    def skipLine(self):
        self.__File.writelines('\n')

    ## @brief Write a defined number of carriage returns to the output file.
    ## @param self
    #  The class instance.
    ## @param numLines
    #  The number of carriage returns to be written.

    def skipLines(self, numLines):
        for i in range(numLines):
            self.skipLine()

    ## @brief Write a line to the output file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The line to be written.

    def writeLine(self, line):
        for i in range(self.__IndentationLevel):
            self.__File.writelines(self.__INDENTATION_SPACES*' ')
        self.__File.writelines('%s\n' % line)

    ## @brief Write an import statement to the output file.
    #
    #  The import statement takes the form "import module" or
    #  "from module import object" depending on the value of the object
    #  input parameter.
    ## @param self
    #  The class instance.
    ## @param module
    #  The name of the module to be imported.
    ## @param object
    #  Optional name of an object to be imported from the module.

    def writeImportStatement(self, module, object=None):
        if object is not None:
            line = 'from %s import %s' % (module, object)
        else:
            line = 'import %s' % module
        self.writeLine(line)
        self.skipLine()

    ## @brief Write a class definition to the output file.
    ## @param self
    #  The class instance.
    ## @param className
    #  The name of the class to be defined.
    ## @param baseClassName
    #  Optional name of a base class from which the actual class inherits.

    def writeClassDefinition(self, className, baseClassName=None):
        self.skipLine()
        if baseClassName is not None:
            line = 'class %s(%s):' % (className, baseClassName)
        else:
            line = 'class %s:' % className
        self.writeLine(line)
        self.skipLine()
        self.indent()

    ## @brief Write a method definition to the output file.
    ## @param self
    #  The class instance.
    ## @param methodName
    #  The name of the method to be defined.
    ## @param parameters
    #  The method parameters.

    def writeMethodDefinition(self, methodName, parameters='(self)'):
        self.skipLine()
        line = 'def %s%s:' % (methodName, parameters)
        self.writeLine(line)
        self.indent()

    ## @brief Write a constructor definition to the output file.
    ## @param self
    #  The class instance.
    ## @param parameters
    #  The constructor parameters.

    def writeConstructorDefinition(self, parameters='(self)'):
        self.writeMethodDefinition('__init__', parameters)

    ## @brief Close the output file.
    ## @param self
    #  The class instance.
    
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
