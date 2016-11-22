import os
import ast
import memoria

with open('out.datum') as cuadruplosFile:
    cuadruplos = cuadruplosFile.readlines()

#read the procedures table and the constant dictionary
procs = ast.literal_eval(cuadruplos[0])
constantes = ast.literal_eval(cuadruplos[1])

#invert the global var dictionary and constant dictionary,
#   the purpose is to have virtual direction as key
varsGlobal = [ (v[0],v[1]) for k, v in procs['global'].items()]
constantsMemory = {v:k for k, v in constantes.items()}

#create global memory
globalMemory = {}
for i,j in varsGlobal:
    if j == None:
        globalMemory[i]=j
    elif j>0:
        for k in range(0,j+1):
            globalMemory[i+k]=None

#set the current quadruple as 2, because first and second element
#   are the procedures table and the constants dictionary
currentQuadruple = 2
isRunning = True #boolean to keep execution loop running
quadrupleOffset = 2 #offset to add when making jump between quadruples

#memory stack, to save memory that is asleep
memoryStack = []
scopeStack = []
saltosSubrutine = []

numToTipo = {   1:'INT',
                2:'FLOAT',
                3:'BOOL',
                4:'CHAR',
                5:'STRING',
                -1:'ERROR'}

def getTypeBasedOnVirtualAddres(address):
    t = address/10000
    t = t % 5
    t = numToTipo[t]

    return t

def createMemory(methodName):
    tempGenMem = memoria.Memoria(110000)
    localGenMem = memoria.Memoria(60000)
    newMemory = {}
    dictionary = procs[methodName][2]
    for k,v in dictionary.items():
        if v[1] == None:
            newMemory[v[0]]=None
        else:
            newMemory[v[0]]=[None for i in range(0, v[1])]
    for i in range(0, len(procs[methodName][4])):
        if procs[methodName][4][i]>0:
            if i<5:
                newMemory[localGenMem.generarEspacioMemoria(numToTipo[i+1],1)]=None
            else:
                newMemory[tempGenMem.generarEspacioMemoria(numToTipo[i%5+1],1)]=None

    return newMemory

currentScope = 'main'
actualMemory = createMemory(currentScope)
#Execution Loop
while isRunning:

    actualCuadruplo = ast.literal_eval(cuadruplos[currentQuadruple])

    if actualCuadruplo[0] == '+':
        #sum operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        #check if the second value is a constant
        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1+oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '-':
        #subtraction operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        #check if the second value is a constant
        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1-oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '*':
        #multiplication operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        #check if the second value is a constant
        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1*oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '/':
        #division operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        #check if the second value is a constant
        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1/oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '^':
        #exponent operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        #check if the second value is a constant
        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1**oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '=':
        #equal operation
        #check if first value is a constant
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        if oper1 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'and':
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1 and oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'or':
        if oper1 == None or oper2 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1 or oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '>':
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        elif actualCuadruplo[1] < 60000:
            oper1 = globalMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]

        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        elif actualCuadruplo[2] < 60000:
            oper2 = globalMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]

        if oper1 == None or oper2 == None:
            print("Error: variable not initialized. > operator.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1 > oper2

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '==':
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        elif actualCuadruplo[1] < 60000:
            oper1 = globalMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]

        if actualCuadruplo[2] > 160000:
            oper2 = constantsMemory[actualCuadruplo[2]]
        elif actualCuadruplo[2] < 60000:
            oper2 = globalMemory[actualCuadruplo[2]]
        else:
            oper2 = actualMemory[actualCuadruplo[2]]

        if oper1 == None or oper2 == None:
            print("Error: variable not initialized. == operator.")
        else:
            actualMemory[actualCuadruplo[3]] = (oper1 == oper2)

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'print':
        #print operation
        print(actualMemory[actualCuadruplo[1]])
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'GOTOF':
        #if the given value is false, go to a certain quadruple
        #if the given value is true, go to the next quadruple
        if actualCuadruplo[1] > 160000:
            oper1 = constantsMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]

        if oper1:
            currentQuadruple = currentQuadruple + 1
        else:
            currentQuadruple = actualCuadruplo[3] + quadrupleOffset
    elif actualCuadruplo[0] == 'GOTO':
        #go to a certain quadruple
        currentQuadruple = actualCuadruplo[3] + quadrupleOffset
    elif actualCuadruplo[0] == 'GOSUB':
        #got to first quadruple of the method
        saltosSubrutine.append(currentQuadruple+1)
        currentQuadruple = actualCuadruplo[3] + quadrupleOffset
    elif actualCuadruplo[0] == 'ERA':
        #generate new memory for the new context
        memoryStack.append(actualMemory)
        scopeStack.append(currentScope)
        currentScope = actualCuadruplo[1]
        actualMemory = createMemory(actualCuadruplo[1])
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'PARAM':
        #assign value to the directions in the new memory
        tempMemoryObject = memoria.Memoria(50000)
        localMemoryObject = memoria.Memoria(110000)
        if actualCuadruplo[1] < 60000:
            paramValue = globalMemory[actualCuadruplo[1]]
        elif actualCuadruplo[1] > 160000:
            paramValue = globalMemory[actualCuadruplo[1]]
        else:
            prevMemory = memoryStack.pop()
            print prevMemory
            print memoryStack
            print actualMemory
            paramValue = prevMemory[actualCuadruplo[1]]
            memoryStack.append(prevMemory)

        if actualCuadruplo[1] >= 60000 and actualCuadruplo[1] < 120000:
            actualMemory[localMemoryObject.generarEspacioMemoria(procs[currentScope][1][actualCuadruplo[3]])]=paramValue
        else:
            actualMemory[tempMemoryObject.generarEspacioMemoria(procs[currentScope][1][actualCuadruplo[3]])]=paramValue

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'VER':
        if  actualMemory[1] < 60000:
            if globalMemory[actualCuadruplo[1]] < actualCuadruplo[2] or globalMemory[actualCuadruplo[1]] > actualCuadruplo[3]:
                print "Runtime Error: Index out of bounds."
                sys.exit()
        elif actualMemory[1] > 160000:
            if constantsMemory[actualCuadruplo[1]] < actualCuadruplo[2] or constantsMemory[actualCuadruplo[1]] > actualCuadruplo[3]:
                print "Runtime Error: Index out of bounds."
                sys.exit()
        else:
            if actualMemory[actualCuadruplo[1]] < actualCuadruplo[2] or actualMemory[actualCuadruplo[1]] > actualCuadruplo[3]:
                print "Runtime Error: Index out of bounds."
                sys.exit()
        currentQuadruple = currentQuadruple + 1

    elif actualCuadruplo[0] == 'RETORNO':
        currentScope = scopeStack.pop()
        actualMemory = memoryStack.pop()
        currentQuadruple = saltosSubrutine.pop()
        print currentQuadruple
        print "retorno currentQuadruple"
    elif actualCuadruplo[0] == 'RETURN':
        if actualCuadruplo[1] > 160000:
            globalMemory[actualCuadruplo[3]] = constantsMemory[actualCuadruplo[1]]
        else:
            globalMemory[actualCuadruplo[3]] = actualMemory[actualCuadruplo[1]]
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'ENDPROG':
        #end of program
        isRunning = False
