import commands

CFG_FILE_PATH = './doxygen.cfg'

tag = commands.getoutput('less ../ChangeLog | grep -A 2 TAG | head -n 2')
tag = tag.split('\n')[1].split(': ')[1].split(',')[0]

cfgFile = file(CFG_FILE_PATH)
cfgFileContent = cfgFile.readlines()
cfgFile.close()

cfgFile = file(CFG_FILE_PATH, 'w')
for line in cfgFileContent:
    if 'PROJECT_NUMBER' in line:
        line = 'PROJECT_NUMBER = %s\n' % tag
    cfgFile.writelines(line)
cfgFile.close()

