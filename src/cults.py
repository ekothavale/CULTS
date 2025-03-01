import sys
import re
import os


def parseFunctions(code: str) -> list:
    functions = []
    l = len(code)
    indices = [m.start() for m in re.finditer('def', code)]
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

def pairFunctionNames(functions: list) -> dict:
    fileNameDict = {}
    functionNameList = []
    for f in functions:
        fName = re.findall(r"(?<=def )[A-z|_][A-z0-9|_]*", f)
        fileNameDict[fName[0] + '.cults'] = f
        functionNameList.append(fName[0])
    return fileNameDict

def getFunctionArgumentFilenames(fileNames: dict) -> dict:
    out = {}
    for dirPath, directories, files in os.walk("tests/", onerror=lambda: print("CULTS assumes tests are in a /tests directory")):
        for file in files:
            if file in fileNames:
                out[file] = fileNames[file]
    return out

def assembleArgs(args: str) -> str:
    count = len(args.split(","))
    if count == 0:
        print(".cults file formatted incorrectly")
        sys.exit(0)
    pieces = list("sys.argv[1]")
    for i in range(count - 1):
        pieces.append(f", sys.argv[{i+2}]")
    return ''.join(pieces), '{' + ''.join(pieces) + '}'


def functional(code: str):
    functions = parseFunctions(code)
    filenameDict = pairFunctionNames(functions)
    imports = re.findall(r'(?<=import )\S+', code)
    functionArgumentFilenamesDict = getFunctionArgumentFilenames(filenameDict)
    fileNames = functionArgumentFilenamesDict.keys()
    print(filenameDict)
    print(functionArgumentFilenamesDict)
    print(fileNames)

    for fileName in fileNames:
        sandbox = open("cultsSandbox.py", "w")
        argFile = open(f"tests/{fileName}", "r")
        argFile.seek(0) # reset file pointer to start of file
        for im in imports:
            sandbox.write(f"import {im}\n")
        sandbox.write("import sys\n\n")
        sandbox.write(functionArgumentFilenamesDict[fileName])
        sandbox.write(f"def CULTSSANDBOX():\n")
        for line in argFile:
            line = line.strip()
            sandbox.write(f"\tprint(\"\033[97m{fileName[:-6]}({line}):\" + '\033[92m', {fileName[:-6]}({line}))\n")
        sandbox.write("if __name__ == \"__main__\":\n\tCULTSSANDBOX()")
        sandbox.close()
        argFile.close()
        os.system("python3 cultsSandbox.py")
    
    os.system("rm cultsSandbox.py")
        
    
    
def main():
    if len(sys.argv) < 2:
        print("Usage Error: cults [filename] ...args...\nType cults -help for info about usage")
        sys.exit(0)
    path = sys.argv[1]
    source = None
    with open(path) as sourceFile:
        if sourceFile == None:
            print("Error: File specifide does not exist\ncults [filename] ...args...\nType cults -help for info about usage")
            sys.exit(0)
        lines = []
        for line in sourceFile:
            if len(lines) > 30000:
                print("Error: Source file excedes 30000 lines. Consider refactoring your code into multiple files")
                sys.exit(0)
            lines.append(line)
        source = ''.join(lines)
    
    if "-f" in sys.argv:
        functional(source)


if __name__ == "__main__":
    main()


def CULTSSANDBOX():
    print(f(sys.argv[1], sys.argv[2]))


# TODO:
# New plan:
#   Opens sandbox once per function
#   creates a series of calls in CULTSSANDBOX for each set of arguments
#   Ex: generates
#   def CULTSSANDBOX():
#       print(func1(1,4))
#       print(func1(3,3333))
#       print(func1(5,-1))
#       print(func1(6,0))
#       print(func1(19,2))
#       print(func1(12,3))
#       ...
