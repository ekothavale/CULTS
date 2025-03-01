# imports
import sys
import re
import os

# user variables
LINELIMIT = 15000 # maximum number of lines in source file

# source code specific items
# python
EXTENSION = ".py"
FUNCTIONDEFINITION = "def "
IMPORTING = "import "
PROGRAMEXECUTION = "python3"

# finds names of all python functions in the desired file and stores in list
def parseFunctions(code: str) -> list:
    functions = []
    l = len(code)
    indices = [m.start() for m in re.finditer(FUNCTIONDEFINITION, code)]
    for index in indices:
        i = index
        while i < l:
            if i == l-1:
                pass
            elif code[i] == '\n' and not code[i+1].isspace():
                break
            i += 1
        functions.append(code[index: i])
    return functions

# takes a list of function names and converts them into their .cults equivalents, then matches them with
# their respective file sourcecode
def pairFunctionNames(functions: list) -> dict:
    fileNameDict = {}
    functionNameList = []
    for f in functions:
        fName = re.findall(rf"(?<={FUNCTIONDEFINITION})[A-z|_][A-z0-9|_]*", f)
        fileNameDict[fName[0] + '.cults'] = f
        functionNameList.append(fName[0])
    return fileNameDict

# filters out filename, source code pairs generated above that don't have an existing .cults file that matches
def getFunctionArgumentFilenames(fileNames: dict) -> dict:
    out = {}
    for dirPath, directories, files in os.walk("tests/", onerror=lambda: print("CULTS assumes tests are in a /tests directory")):
        for file in files:
            if file in fileNames:
                out[file] = fileNames[file]
    return out

def pythonTest(fileName, sandbox, argFile, imports, functionArgumentFilenamesDict):
    for im in imports:
        sandbox.write(f"import {im}\n")
    sandbox.write(functionArgumentFilenamesDict[fileName])
    sandbox.write("def CULTSSANDBOX():\n")
    for line in argFile:
        line = line.strip()
        sandbox.write(f"\tprint(\"\033[97m{fileName[:-6]}({line}):\" + '\033[92m', {fileName[:-6]}({line}))\n")
    sandbox.write("if __name__ == \"__main__\":\n\tCULTSSANDBOX()")
    sandbox.close()
    argFile.close()

# takes source code as input and tests each function with a corresponding .cults file
def functional(code: str):
    functions = parseFunctions(code)
    filenameDict = pairFunctionNames(functions)
    imports = re.findall(r'(?<=import )\S+', code)
    functionArgumentFilenamesDict = getFunctionArgumentFilenames(filenameDict)
    fileNames = functionArgumentFilenamesDict.keys()

    for fileName in fileNames:
        sandbox = open(f"cultsSandbox{EXTENSION}", "w")
        argFile = open(f"tests/{fileName}", "r")
        argFile.seek(0) # reset file pointer to start of file
        pythonTest(fileName, sandbox, argFile, imports, functionArgumentFilenamesDict)
        os.system(f"{PROGRAMEXECUTION} cultsSandbox{EXTENSION}")
    
    os.system(f"rm cultsSandbox{EXTENSION}")
        
    
    
def main():
    if len(sys.argv) < 2:
        print("Usage Error: cults [filename] ...args...\nType cults -help for info about usage")
        sys.exit(0)
    path = sys.argv[1]
    source = None
    # reads in source code from file specified in command line
    with open(path) as sourceFile:
        if sourceFile == None:
            print("Error: File specifide does not exist\ncults [filename] ...args...\nType cults -help for info about usage")
            sys.exit(0)
        lines = []
        for line in sourceFile:
            if len(lines) > LINELIMIT:
                print(f"Error: Source file excedes {LINELIMIT} lines. Consider refactoring your code into multiple files")
                sys.exit(0)
            lines.append(line)
        source = ''.join(lines)
    
    if "-f" in sys.argv:
        functional(source)


if __name__ == "__main__":
    main()
