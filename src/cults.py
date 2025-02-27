import sys
import re
import os
import time
import subprocess


test = """
import sys
import os
import time
import math


def func1(x, y):
    return x * y

def func2(str1, str2):
    str1 = 'replaced'
    print(str1 + ' ' + str2)

    str3 = "this is a part of the function too"

def func_3():
    a = math.cos(1)
    b = math.sin(1)
    print(a * a + b * b)
    return
"""

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
    out = {}
    for f in functions:
        fName = re.findall(r"(?<=def )[A-z|_][A-z0-9|_]*", f)
        out[fName[0]] = f
    return out

def getFunctionArgumentFilenames(fileNames: list) -> list:
    out = []
    for dirPath, directories, files in os.walk("tests/", onerror=lambda x: print("CULTS assumes tests are in a /tests directory")):
        for file in files:
            if file.endswith(".cults") and file[:-6] in fileNames:
                out.append(file)
    return out

def functional(code: str):
    functions = parseFunctions(code)
    funcDict = pairFunctionNames(functions)
    funcNames = list(funcDict.keys())
    imports = re.findall(r'(?<=import )\S+', code)
    functionArgumentFilenames = getFunctionArgumentFilenames(funcNames)
    print(functionArgumentFilenames)
    for i in range(len(functionArgumentFilenames)):
        argFile = open(f"tests/{functionArgumentFilenames[i]}", "r")
        for line in argFile:
            line = line.rstrip("\n")
            sandbox = open("cultsSandbox.py", "w")
            for im in imports:
                sandbox.write(f"import {im}\n")
            sandbox.write(functions[i])
            sandbox.write(f"\nprint(f\"{funcNames[i]}({line}):\", {funcNames[i]}({line}))\n")
            subprocess.run(["python3", "cultsSandbox.py"])
    sandbox.close()
    argFile.close()
    #subprocess.run(["rm", "cultsSandbox.py"])
        
    
    
def main():
    if len(sys.argv) < 2:
        print("Usage Error: cults [filename] ...args...\nType cults -help for info about usage")
        sys.exit(0)
    path = sys.argv[1]
    
    if "-f" in sys.argv:
        functional(test)


if __name__ == "__main__":
    main()