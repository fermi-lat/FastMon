## @package pCodeGenerator
## @brief Module containing useful functions for dinamically writing python
#  code (used in iterator writers and contribution writers).

import os
import time
import sys

from pGlobals     import *
from pAsciiWriter import pAsciiWriter


## @brief Implementation of the code generator.

class pCodeGenerator(pAsciiWriter):

    ## @brief Constructor.
    ## @param self
    #  The class instance.

    def __init__(self, outputFilePath = None):
        pAsciiWriter.__init__(self, outputFilePath)

    ## @brief Open the output file.
    ## @param self
    #  The class instance.
    ## @param filePath
    #  The path to the file to be created.

    def openFile(self, outputFileName):
        if FASTMON_DIR_VAR_NAME in os.environ:
            outputFilePath = os.path.join(os.environ[FASTMON_DIR_VAR_NAME],\
                                          outputFileName)
        else:
            sys.exit('Environmental variable %s not found. Exiting...' %\
                     FASTMON_DIR_VAR_NAME)
        pAsciiWriter.openFile(self, outputFilePath, 'w')
        self.writeComment('Written by pCodeGenerator on %s' % time.asctime())
        self.writeComment('Any change to this file will be lost.')
        self.newLine()

    ## @brief Write a comment in the output file.
    ## @param self
    #  The class instance.
    ## @param line
    #  The actual comment.

    def writeComment(self, line):
        self.writeLine('# %s' % line)

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
        self.newLine()

    ## @brief Write a class definition to the output file.
    ## @param self
    #  The class instance.
    ## @param className
    #  The name of the class to be defined.
    ## @param baseClassName
    #  Optional name of a base class from which the actual class inherits.

    def writeClassDefinition(self, className, baseClassName=None):
        self.newLine()
        if baseClassName is not None:
            line = 'class %s(%s):' % (className, baseClassName)
        else:
            line = 'class %s:' % className
        self.writeLine(line)
        self.newLine()
        self.indent()

    ## @brief Write a method definition to the output file.
    ## @param self
    #  The class instance.
    ## @param methodName
    #  The name of the method to be defined.
    ## @param parameters
    #  The method parameters.

    def writeMethodDefinition(self, methodName, parameters='(self)'):
        self.newLine()
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

    

if __name__ == '__main__':
    g = pCodeGenerator()
    g.openFile('python_test.py')
    g.writeClassDefinition('A', 'B')
    g.writeConstructorDefinition()
    g.writeLine('pass')
    g.backup()
    g.newLine()
    g.writeMethodDefinition('test', '(self, value)')
    g.writeLine('a = value')
    g.closeFile()
