import os
import ast
import memoria
import sys
import matplotlib.pyplot as plt

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
                0:'STRING',
                5:'STRING',
                -1:'ERROR'}

def getTypeBasedOnVirtualAddres(address):
    t = address/10000
    t = t % 5
    t = numToTipo[t]

    return t

def getNumTypeBasedOnVirtualAddres(address):
    t = address/10000
    t = t % 5

    return t

def createMemory(methodName):
    tempGenMem = memoria.Memoria(110000)
    localGenMem = memoria.Memoria(50000)
    newMemory = {}
    dictionary = procs[methodName][2]

    for i in range(0, len(procs[methodName][4])):
        for j in range(0, procs[methodName][4][i]):
            if i<5:
                newMemory[localGenMem.generarEspacioMemoria(numToTipo[i+1],1)]=None
            else:
                newMemory[tempGenMem.generarEspacioMemoria(numToTipo[i%5+1],1)]=None

    return newMemory

currentScope = 'main'
actualMemory = createMemory(currentScope)

def getVAStoredInAnotherVA(quad):
    for i in range(0,len(quad)):
        if type(quad[i]) is list:
            quad[i] = actualMemory[quad[i][0]]

    return quad

#Execution Loop
while isRunning:

    actualCuadruplo = ast.literal_eval(cuadruplos[currentQuadruple])
    actualCuadruplo = getVAStoredInAnotherVA(actualCuadruplo)

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
        elif actualCuadruplo[1] < 60000:
            oper1 = globalMemory[actualCuadruplo[1]]
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
        elif actualCuadruplo[1] < 60000:
            oper1 = globalMemory[actualCuadruplo[1]]
        else:
            oper1 = actualMemory[actualCuadruplo[1]]
        if oper1 == None:
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'and':
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
            print("Error: variable not initialized.")
        else:
            actualMemory[actualCuadruplo[3]] = oper1 and oper2
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'or':
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
    elif actualCuadruplo[0] == '<':
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
            print("Error: variable not initialized. < operator.")
        else:
            actualMemory[actualCuadruplo[3]] = (oper1 < oper2)

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '>=':
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
            print("Error: variable not initialized. >= operator.")
        else:
            actualMemory[actualCuadruplo[3]] = (oper1 >= oper2)

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '<=':
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
            print("Error: variable not initialized. <= operator.")
        else:
            actualMemory[actualCuadruplo[3]] = (oper1 <= oper2)

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == '<>':
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
            print("Error: variable not initialized. <> operator.")
        else:
            actualMemory[actualCuadruplo[3]] = (oper1 != oper2)

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'SCATTERCHART' or actualCuadruplo[0] == 'LINECHART' or actualCuadruplo[0] == 'BARCHART':
        chartType = actualCuadruplo[0]
        dirBaseDatosX = actualCuadruplo[1]
        dirBaseDatosY = actualCuadruplo[2]
        tamDatosX = actualCuadruplo[3]

        currentQuadruple = currentQuadruple + 1
        actualCuadruplo = ast.literal_eval(cuadruplos[currentQuadruple])
        actualCuadruplo = getVAStoredInAnotherVA(actualCuadruplo)

        dirChartTitle = actualCuadruplo[3]
        dirChartAxisXTitle = actualCuadruplo[1]
        dirChartAxisYTitle = actualCuadruplo[2]

        if dirChartTitle > 160000:
            chartTitle = constantsMemory[dirChartTitle]
        elif dirChartTitle < 60000:
            chartTitle = globalMemory[dirChartTitle]
        else:
            chartTitle = actualMemory[dirChartTitle]

        if dirChartAxisXTitle > 160000:
            xLabel = constantsMemory[dirChartAxisXTitle]
        elif dirChartAxisXTitle < 60000:
            xLabel = globalMemory[dirChartAxisXTitle]
        else:
            xLabel = actualMemory[dirChartAxisXTitle]

        if dirChartAxisYTitle > 160000:
            yLabel = constantsMemory[dirChartAxisYTitle]
        elif dirChartAxisYTitle < 60000:
            yLabel = globalMemory[dirChartAxisYTitle]
        else:
            yLabel = actualMemory[dirChartAxisYTitle]

        arrDatosX = []
        arrDatosY = []
        for i in range(0, tamDatosX):
            if dirBaseDatosX < 60000:
                arrDatosX.append(globalMemory[dirBaseDatosX+i])
            else:
                arrDatosX.append(actualMemory[dirBaseDatosX+i])
            if dirBaseDatosY < 60000:
                arrDatosY.append(globalMemory[dirBaseDatosY+i])
            else:
                arrDatosY.append(actualMemory[dirBaseDatosY+i])

        chart = plt.figure(chartTitle)
        if chartType == 'SCATTERCHART':
            chart = plt.scatter(arrDatosX, arrDatosY)
        elif chartType == 'BARCHART':
            chart = plt.bar(arrDatosX, arrDatosY)
        else:#linechart
            chart = plt.plot(arrDatosX, arrDatosY)

        chart = plt.xlabel(xLabel)
        chart = plt.ylabel(yLabel)

        currentQuadruple = currentQuadruple + 1

    elif actualCuadruplo[0] == 'PIECHART':
        dirBaseDatos = actualCuadruplo[1]
        dirBaseLabels = actualCuadruplo[2]
        tamDatos = actualCuadruplo[3]

        currentQuadruple = currentQuadruple + 1
        actualCuadruplo = ast.literal_eval(cuadruplos[currentQuadruple])
        actualCuadruplo = getVAStoredInAnotherVA(actualCuadruplo)

        dirChartTitle = actualCuadruplo[3]

        if dirChartTitle > 160000:
            chartTitle = constantsMemory[dirChartTitle]
        elif dirChartTitle < 60000:
            chartTitle = globalMemory[dirChartTitle]
        else:
            chartTitle = actualMemory[dirChartTitle]

        arrDatos = []
        arrLabels = []
        for i in range(0, tamDatos):
            if dirBaseDatos < 60000:
                arrDatos.append(globalMemory[dirBaseDatos+i])
            else:
                arrDatos.append(actualMemory[dirBaseDatos+i])
            if dirBaseLabels < 60000:
                arrLabels.append(globalMemory[dirBaseLabels+i])
            else:
                arrLabels.append(actualMemory[dirBaseLabels+i])

        ch1 = plt.figure(chartTitle)
        ch1 = plt.pie(arrDatos, labels=arrLabels)
        #plt.show()
        currentQuadruple = currentQuadruple + 1

    elif actualCuadruplo[0] == 'print':
        #print operation
        if actualCuadruplo[1] > 160000:
            print(constantsMemory[actualCuadruplo[1]])
        elif actualCuadruplo[1] < 60000:
            print(globalMemory[actualCuadruplo[1]])
        else:
            print(actualMemory[actualCuadruplo[1]])
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'READ':
        inputData = raw_input()
        castedInput = inputData
        if getNumTypeBasedOnVirtualAddres(actualCuadruplo[1]) == 1:
            castedInput = int(inputData)
        elif getNumTypeBasedOnVirtualAddres(actualCuadruplo[1]) == 2:
            castedInput = float(inputData)
        elif getNumTypeBasedOnVirtualAddres(actualCuadruplo[1]) == 3:
            castedInput = ast.literal_eval(inputData)
        elif len(inputData) == 1:
            if getTypeBasedOnVirtualAddres(actualCuadruplo[1]) == 4:
                print("Error: char is only allowed to hold 1 character")

        if actualCuadruplo[1] > 160000:
            print("Error: a value read from keyboard can not be assigned to a constant")
        elif actualCuadruplo[1] < 60000:
            globalMemory[actualCuadruplo[1]] = castedInput
        else:
            actualMemory[actualCuadruplo[1]] = castedInput

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
        tempMemoryObject = memoria.Memoria(110000)
        localMemoryObject = memoria.Memoria(50000)
        if actualCuadruplo[1] < 60000:
            paramValue = globalMemory[actualCuadruplo[1]]
        elif actualCuadruplo[1] > 160000:
            paramValue = constantsMemory[actualCuadruplo[1]]
        else:
            prevMemory = memoryStack.pop()
            paramValue = prevMemory[actualCuadruplo[1]]
            memoryStack.append(prevMemory)

        if actualCuadruplo[1] >= 60000 and actualCuadruplo[1] < 120000:
            actualMemory[localMemoryObject.generarEspacioMemoria(procs[currentScope][1][actualCuadruplo[3]])]=paramValue
        else:
            actualMemory[tempMemoryObject.generarEspacioMemoria(procs[currentScope][1][actualCuadruplo[3]])]=paramValue

        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'VER':
        if  actualCuadruplo[1] < 60000:
            if globalMemory[actualCuadruplo[1]] < actualCuadruplo[2] or globalMemory[actualCuadruplo[1]] > actualCuadruplo[3]:
                print "Runtime Error: Index out of bounds."
                sys.exit()
        elif actualCuadruplo[1] > 160000:
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
    elif actualCuadruplo[0] == 'RETURN':
        if actualCuadruplo[1] > 160000:
            globalMemory[actualCuadruplo[3]] = constantsMemory[actualCuadruplo[1]]
        else:
            globalMemory[actualCuadruplo[3]] = actualMemory[actualCuadruplo[1]]
        currentQuadruple = currentQuadruple + 1
    elif actualCuadruplo[0] == 'ENDPROG':
        #end of program
        isRunning = False
        plt.show()
