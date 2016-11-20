import sys
import ply.lex as lex
import ply.yacc as yacc
import semantic_cube as scube
import memoria as mem

#Lenguaje Datum

#Palabras reservadas
reserved = {
    'program' : 'PROGRAM',
    'if' : 'IF',
    'else' : 'ELSE',
    'print' : 'PRINT',
    'int' : 'INT',
    'float' : 'FLOAT',
    'string' : 'STRING',
    'char' : 'CHAR',
    'bool' : 'BOOL',
    'Vec' : 'VEC',
    'void' : 'VOID',
    'while' : 'WHILE',
    'barchart' : 'BARCHART',
    'scatterchart' : 'SCATTERCHART',
    'linechart' : 'LINECHART',
    'piechart' : 'PIECHART',
    'main' : 'MAIN',
    'and' : 'AND',
    'or' : 'OR',
    'return' : 'RETURN',
    'read' : 'READ',
    'True' : 'TRUE',
    'False' : 'FALSE'
}

#Tokens
tokens = [
    'ID',
    'CTE_INT',
    'CTE_FLOAT',
    'CTE_STR',
    'CTE_CHAR',
    'LESSEQUAL',
    'MOREEQUAL',
    'DEQUAL',
    'DIFF'
]

tokens += list(reserved.values())

t_CTE_INT = r'(\+|-)?[0-9]+'
t_CTE_FLOAT = r'(\+|-)?[0-9]*\.[0-9]+'
t_CTE_STR = r'\".*\"'
t_CTE_CHAR = r'\'.\''
t_LESSEQUAL = r'<='
t_MOREEQUAL = r'>='
t_DEQUAL = r'=='
t_DIFF = r'<>'

literals = ";:,\{\}\<\>\+\-\*\/\(\)=\[\]"

t_ignore = " \t"

lineNumber = 1

def t_newline(t):
    r'\n+'
    global lineNumber
    lineNumber += len(t.value)
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'(_*[a-zA-Z]+_*[0-9]*_*)+'
    #Check for reserved words
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    print("Caracter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)
    sys.exit()

#Build lexer
lex.lex()

#diccionario para convertir el numero del tipo al string del tipo
numToTipo = {   1:'INT',
                2:'FLOAT',
                3:'BOOL',
                4:'CHAR',
                5:'STRING',
                -1:'ERROR'}

#Tabla de constantes
constantes = {}

#Tabla Procedimiento
procs = {}

#Variable to save the current scope
current_scope = 'global'

#Variable to check if we are dealing with parameters
inParams = False

#Lista de cuadruplos generados.
#Nota: cada cuadruplo lista de 4 elementos.
cuadruplos = []
contCuadruplos = 0

#Pilas utilizadas en generacion de cuadruplos
pilaO = []
pOper = []
pSaltos = []
pTipos = []

#Pila de variables dimensionadas
pDim = []
varDim = []
varMemDim = []

#Contadores dir mem
contTemp=0

#Contador de parametros
contParametros = []
scopeParametros = []

#Inicios memoria
inicioGlobales = 0
inicioLocal = 50000
inicioTemp = 110000
inicioCTE = 160000

#Memoria
memGlobales = mem.Memoria(inicioGlobales)
memConstantes = mem.Memoria(inicioCTE)

#Objetos memoria virtual para funciones
func_memLocal = mem.Memoria(inicioLocal)
func_memTemp = mem.Memoria(inicioTemp)

#Gramatica
def p_progam(p):
    '''
    program : t_prog ID ';' declare_vars prog_body
    '''
    cuadruplos.append(['ENDPROG',None, None, None])
    global procs
    print 'Tabla de Procedimientos:'
    print(procs)
    print ''
    global constantes
    print 'Tabla vars globales'
    print procs['global']
    print 'Tabla vars globales invertida'
    invGlobVars = { v[0]: [k,v[1]] for k, v in procs['global'].items()}
    print invGlobVars
    print 'Tabla de constantes:'
    print constantes
    print 'Tabla de constantes invertida'
    invConstDict = {v:k for k, v in constantes.items()}
    print invConstDict
    print ''

def p_t_prog(p):
    '''
    t_prog : PROGRAM
    '''
    procs['global'] = {}

def p_declare_vars(p):
    '''
    declare_vars :  vars declare_vars
                    | empty
    '''

def p_vars(p):
    '''
    vars :  var initialize_var ';'
            | vector
    '''

def p_var(p):
    '''
    var : tipo ID
    '''
    global procs
    if current_scope == 'global':
        if p[2] in procs[current_scope].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            procs[current_scope][p[2]]=[memGlobales.generarEspacioMemoria(p[1]), None]

    else:
        if p[2] in procs['global'].keys() or p[2] in procs[current_scope][2].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            global inParams
            if inParams:
                procs[current_scope][1].append(p[1])
            procs[current_scope][2][p[2]] = [func_memLocal.generarEspacioMemoria(p[1]), None]
            print procs

def p_initialize_var(p):
    '''
    initialize_var : '=' expresion
                    | empty
    '''

def p_vector(p):
    '''
    vector : VEC tipo ID '[' cte_int ']' ';'
    '''
    pilaO.pop()
    tipo = pTipos.pop()
    tamVec = int(p[5])
    limiteSuperior = tamVec - 1
    if current_scope == 'global':
        if p[3] in procs[current_scope].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            memVar = memGlobales.generarEspacioMemoria(tipo, tamVec)
            varDim.append(p[3])
            varMemDim.append(memVar)
            procs[current_scope][p[3]]=[memVar, limiteSuperior]

    else:
        if p[3] in procs['global'].keys() or p[3] in procs[current_scope][2].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            global inParams
            if inParams:
                procs[current_scope][1].append(p[1])
            memVar = func_memLocal.generarEspacioMemoria(tipo, tamVec)
            varDim.append(p[3])
            varMemDim.append(memVar)
            procs[current_scope][2][p[3]] = [memVar, limiteSuperior]

def p_tipo(p):
    '''
    tipo : INT
            | FLOAT
            | STRING
            | CHAR
            | BOOL
    '''
    p[0] = p[1].upper()

def p_constants(p):
    '''
    constants : cte_int
            | cte_float
            | cte_str
            | cte_char
            | cte_bool
    '''
def p_cte_int(p):
    '''
    cte_int : CTE_INT
    '''
    if(p[1] not in constantes.keys()):
        #constantes[p[1]] = 'INT'
        constantes[p[1]] = memConstantes.generarEspacioMemoria('INT')
    pilaO.append(constantes[p[1]])
    pTipos.append('INT')
    p[0] = p[1]

def p_cte_float(p):
    '''
    cte_float : CTE_FLOAT
    '''
    if(p[1] not in constantes.keys()):
        #constantes[p[1]] = 'FLOAT'
        constantes[p[1]] = memConstantes.generarEspacioMemoria('FLOAT')
    pilaO.append(constantes[p[1]])
    pTipos.append('FLOAT')

def p_cte_bool(p):
    '''
    cte_bool : TRUE
            | FALSE
    '''
    if(p[1] not in constantes.keys()):
        #constantes[p[1]] = 'BOOL'
        constantes[p[1]] = memConstantes.generarEspacioMemoria('BOOL')
    pilaO.append(constantes[p[1]])
    pTipos.append('BOOL')

def p_cte_char(p):
    '''
    cte_char : CTE_CHAR
    '''
    if(p[1] not in constantes.keys()):
        #constantes[p[1]] = 'CHAR'
        constantes[p[1]] = memConstantes.generarEspacioMemoria('CHAR')
    pilaO.append(constantes[p[1]])
    pTipos.append('CHAR')

def p_cte_str(p):
    '''
    cte_str : CTE_STR
    '''
    if(p[1] not in constantes.keys()):
        #constantes[p[1]] = 'STRING'
        constantes[p[1]] = memConstantes.generarEspacioMemoria('STRING')
    pilaO.append(constantes[p[1]])
    pTipos.append('STRING')

def p_prog_body(p):
    '''
    prog_body : '{' funciones main_body '}'
    '''

def p_main_body(p):
    '''
    main_body : t_main '(' ')' '{' declare_vars estatuto '}'
    '''
    global current_scope
    global procs
    procs[current_scope][4].append(func_memLocal.intCount+1)
    procs[current_scope][4].append(func_memLocal.floatCount+1)
    procs[current_scope][4].append(func_memLocal.boolCount+1)
    procs[current_scope][4].append(func_memLocal.charCount+1)
    procs[current_scope][4].append(func_memLocal.stringCount+1)

    procs[current_scope][4].append(func_memTemp.intCount + 1)
    procs[current_scope][4].append(func_memTemp.floatCount + 1)
    procs[current_scope][4].append(func_memTemp.boolCount + 1)
    procs[current_scope][4].append(func_memTemp.charCount + 1)
    procs[current_scope][4].append(func_memTemp.stringCount + 1)

    current_scope = 'global'
    #creo que hay que marcar end aqui

def p_t_main(p):
    '''
    t_main : MAIN
    '''
    global procs
    scope = p[1]
    if scope in procs:
        print('ERROR: Funcion repetida en linea %d.' % lineNumber)
        sys.exit()
    global current_scope
    current_scope = scope
    global func_memLocal, func_memTemp
    func_memLocal = mem.Memoria(inicioLocal)
    func_memTemp = mem.Memoria(inicioTemp)
    procs[current_scope] = [p[1], [], {}, contCuadruplos, []]

def p_funciones(p):
    '''
    funciones : t_new_func '(' t_inParams params t_outParams ')' '{' declare_vars inicio_cuadruplo estatuto return_body '}' end_func funciones
                | t_new_voidFunc '(' t_inParams params t_outParams ')' '{' declare_vars inicio_cuadruplo estatuto '}' end_func funciones
                | empty
    '''
    global current_scope
    current_scope = 'global'

def p_inicio_cuadruplo(p):
    '''
    inicio_cuadruplo :
    '''
    procs[current_scope][3] = contCuadruplos

def p_end_func(p):
    '''
    end_func :
    '''
    #Liberar tabla de variables del procedimiento
    global procs
    if current_scope != 'global':
        global procs
        procs[current_scope][4].append(func_memLocal.intCount+1)
        procs[current_scope][4].append(func_memLocal.floatCount+1)
        procs[current_scope][4].append(func_memLocal.boolCount+1)
        procs[current_scope][4].append(func_memLocal.charCount+1)
        procs[current_scope][4].append(func_memLocal.stringCount+1)

        procs[current_scope][4].append(func_memTemp.intCount + 1)
        procs[current_scope][4].append(func_memTemp.floatCount + 1)
        procs[current_scope][4].append(func_memTemp.boolCount + 1)
        procs[current_scope][4].append(func_memTemp.charCount + 1)
        procs[current_scope][4].append(func_memTemp.stringCount + 1)
    cuadruplos.append(['RETORNO', None, None, None])
    global contCuadruplos
    contCuadruplos += 1

def p_t_inParams(p):
    '''
    t_inParams :
    '''
    global inParams
    inParams = True

def p_t_outParams(p):
    '''
    t_outParams :
    '''
    global inParams
    inParams = False

def declaracionMetodo(tipo, scope):
    global current_scope
    global procs
    global func_memLocal, func_memTemp
    if scope in procs or scope in procs['global']:
        print('ERROR: Nombre de variable repetida en linea %d.' % lineNumber)
        sys.exit()
    current_scope = scope
    func_memLocal = mem.Memoria(inicioLocal)
    func_memTemp = mem.Memoria(inicioTemp)
    procs[current_scope] = [tipo, [], {}, contCuadruplos, []]

def p_t_new_func(p):
    '''
    t_new_func : func_tipo ID
    '''
    scope = p[2]
    declaracionMetodo(p[1], scope)
    #Crear una variable para el valor de retorno de la funcion
    if p[2] in procs['global'].keys():
        print("ERROR: variable/funcion con el mismo nombre declarada dos veces en linea %d." % lineNumber)
        sys.exit()
    else:
        procs['global'][p[2]] = [memGlobales.generarEspacioMemoria(p[1]), None]

def p_t_new_voidFunc(p):
    '''
    t_new_voidFunc : VOID ID
    '''
    declaracionMetodo(p[1], p[2])

def p_func_tipo(p):
    '''
    func_tipo : tipo
    '''
    p[0] = p[1].upper()

def p_params(p):
    '''
    params : var params1
            | empty
    '''

def p_params1(p):
    '''
    params1 : ',' params
            | empty
    '''

def p_return_body(p):
    '''
    return_body : RETURN expresion return_accion1 ';'
    '''

def p_return_accion1(p):
    '''
    return_accion1 :
    '''
    valorRetorno = pilaO.pop()
    tipoRetorno = pTipos.pop()
    tipoFunc = procs[current_scope][0]
    if scube.semantic_cube[tipoFunc][tipoRetorno]['='] > 0:
        dirCurrScope = procs['global'][current_scope][0]
        nuevoCuadruplo = ['RETURN', valorRetorno, None, dirCurrScope]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1
    else:
        print 'ERROR: Type mismatch in line %d.' % lineNumber
        sys.exit()

def p_bloque(p):
    '''
    bloque : '{' estatuto '}'
    '''

def p_estatuto(p):
    '''
    estatuto : estatuto1 estatuto2
    '''

def p_estatuto1(p):
    '''
    estatuto1 : asignacion
                | condicion
                | repeticion
                | escritura
                | lectura
                | graficar
                | expresion ';'
    '''

def p_estatuto2(p):
    '''
    estatuto2 : estatuto
                | empty
    '''

def p_asignacion(p):
    '''
    asignacion : asignacion_accion1 asignacion2 asignacion_accion2 expresion ';'
    '''
    resultado = pilaO.pop()
    tipoResultado = pTipos.pop()
    asignado = pilaO.pop()
    tipoAsignado = pTipos.pop()
    oper = pOper.pop()
    if scube.semantic_cube[tipoAsignado][tipoResultado][oper] > 0:
        nuevoCuadruplo = [oper, resultado, None, asignado]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1
    else:
        print 'ERROR: Type mismatch in line %d.' % lineNumber
        sys.exit()

def p_asignacion_accion1(p):
    '''
    asignacion_accion1 : ID
    '''
    if p[1] in procs[current_scope][2].keys():
        variable = procs[current_scope][2][p[1]][0]
        tipo = variable
        tipo = tipo/10000
        tipo = tipo % 5
        tipo = numToTipo[tipo]
        pilaO.append(variable)
    elif p[1] in procs['global'].keys():
        variable = procs['global'][p[1]][0]
        tipo = variable
        tipo = tipo/10000
        tipo = numToTipo[tipo]
        pilaO.append(variable)
    else:
        print 'ERROR: %s Variable no declarada en linea %d.' % (str(p[1]), lineNumber)
        sys.exit()
    pTipos.append(tipo)

def p_asignacion_accion2(p):
    '''
    asignacion_accion2 : '='
    '''
    pOper.append(p[1])

def p_asignacion2(p):
    '''
    asignacion2 : opc_vector
                | empty
    '''

def p_opc_vector(p):
    '''
    opc_vector : '[' dim_accion2 exp ']'
    '''
    resulExp = pilaO.pop()
    resulTipo = pTipos.pop()
    variable = pDim[-1]
    if variable in procs['global']:
        limSup = procs['global'][variable][1]
    elif variable in procs[current_scope][2]:
        limSup = procs[current_scope][2][variable][1]

    nuevoCuadruplo = ['VER', resulExp, 0, limSup]
    cuadruplos.append(nuevoCuadruplo)
    global contCuadruplos
    contCuadruplos += 1
    if resulTipo != 'INT':
        print 'ERROR: Type mismatch in line %d.' % lineNumber
        sys.exit()
    else:
        temp = func_memTemp.generarEspacioMemoria('INT')
        nuevoCuadruplo = ['+', temp, resulExp, temp]
        cuadruplos.append(nuevoCuadruplo)
        contCuadruplos += 1
        pilaO.append([temp])
        pOper.pop()
        pDim.pop()

def p_dim_accion2(p):
    '''
    dim_accion2 :
    '''
    variable = pilaO.pop()

    if variable not in varMemDim:
        print 'ERROR: Variable no dimensionada en linea %d.' % lineNumber
        sys.exit()
    else:
        indiceVar = varMemDim.index(variable)
        pDim.append(varDim[indiceVar])
        pOper.append('#')

def p_condicion(p):
    '''
    condicion : IF '(' expresion ')' condicion_accion1 bloque condicion1 condicion_accion3
    '''

def p_condicion_accion1(p):
    '''
    condicion_accion1 :
    '''
    aux = pTipos.pop()
    if aux != 'BOOL':
        print('ERROR: Type mismatch in line %d.' % lineNumber)
        sys.exit()
    else:
        resultado = pilaO.pop()
        #Generar el cuadruplo
        cuadruplos.append(['GOTOF', resultado, None, None])
        global contCuadruplos
        contCuadruplos += 1

        pSaltos.append(contCuadruplos - 1)

def p_condicion1(p):
    '''
    condicion1 : ELSE condicion_accion2 bloque
                | empty
    '''

def p_condicion_accion2(p):
    '''
    condicion_accion2 :
    '''
    cuadruplos.append(['GOTO', None, None, None])
    global contCuadruplos
    contCuadruplos += 1
    falso = pSaltos.pop()
    cuadruplos[falso][3] = contCuadruplos

    pSaltos.append(contCuadruplos - 1)

def p_condicion_accion3(p):
    '''
    condicion_accion3 :
    '''
    fin = pSaltos.pop()
    cuadruplos[fin][3] = contCuadruplos

def p_repeticion(p):
    '''
    repeticion : WHILE repeticion_accion1 '(' expresion ')' repeticion_accion2 bloque repeticion_accion3
    '''

def p_repeticion_accion1(p):
    '''
    repeticion_accion1 :
    '''
    pSaltos.append(contCuadruplos)

def p_repeticion_accion2(p):
    '''
    repeticion_accion2 :
    '''
    aux = pTipos.pop()
    if aux != 'BOOL':
        print('ERROR: Type mismatch in %d.' % lineNumber)
        sys.exit()
    else:
        resultado = pilaO.pop()
        #Generar cuadruplo
        cuadruplos.append(['GOTOF', resultado, None, None])
        global contCuadruplos
        contCuadruplos += 1

        pSaltos.append(contCuadruplos - 1)

def p_repeticion_accion3(p):
    '''
    repeticion_accion3 :
    '''
    falso = pSaltos.pop()
    retorno = pSaltos.pop()

    cuadruplos.append(['GOTO', None, None, retorno])
    global contCuadruplos
    contCuadruplos += 1

    cuadruplos[falso][3] = contCuadruplos

def p_escritura(p):
    '''
    escritura : PRINT '(' expresion ')' ';'
    '''
    resultado = pilaO.pop()
    pTipos.pop()
    nuevoCuadruplo = [p[1], resultado, None, None]
    cuadruplos.append(nuevoCuadruplo)
    global contCuadruplos
    contCuadruplos += 1

def p_lectura(p):
    '''
    lectura : READ '(' ID ')' ';'
    '''
    if p[3] in procs[current_scope][2].keys() or p[3] in procs['global'].keys():
        nuevoCuadruplo = ['READ', p[3], None, None]
        global contCuadruplos
        cuadruplos.append(nuevoCuadruplo)
        contCuadruplos += 1
    else:
        print 'ERROR: Variable no declarada en linea %d.' % lineNumber

def p_graficar(p):
    '''
    graficar : graficar2 ';'
    '''

def p_graficar2(p):
    '''
    graficar2 : charts '(' ID ',' ID ',' title ',' title ',' title ')'
                | pie_chart
    '''

def p_charts(p):
    '''
    charts : BARCHART
            | SCATTERCHART
            | LINECHART
    '''

def p_pie_chart(p):
    '''
    pie_chart : PIECHART '(' ID ',' ID ',' title ')'
    '''

def p_title(p):
    '''
    title : ID
            | CTE_STR
    '''

def p_expresion(p):
    '''
    expresion : exp codigoExpAccion9 expresion1
    '''

def p_codigoExpAccion9(p):
    '''
    codigoExpAccion9 :
    '''
    if len(pOper) > 0:
        if (pOper[len(pOper)-1] == '>' or pOper[len(pOper)-1] == '<' or
            pOper[len(pOper)-1] == '>=' or pOper[len(pOper)-1] == '=>' or
            pOper[len(pOper)-1] == '==' or pOper[len(pOper)-1] == '<>'):
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            tipoSCube = scube.semantic_cube[tipoOp1][tipoOp2][operador]
            if tipoSCube > 0:
                operando2 = pilaO.pop()
                operando1 = pilaO.pop()
                global contTemp
                resultado = func_memTemp.generarEspacioMemoria(numToTipo[tipoSCube])
                nuevoCuad = [operador, operando1, operando2, resultado]
                global contCuadruplos
                contCuadruplos += 1
                global cuadruplos
                cuadruplos.append(nuevoCuad)
                #regresar temp al avail si se desocupo
                pilaO.append(resultado)
                pTipos.append(numToTipo[scube.semantic_cube[tipoOp1][tipoOp2][operador]])

            else:
                print("ERROR: operacion " + operador + " con tipos incompatibles.")
                sys.exit()

def p_expresion1(p):
    '''
    expresion1 : op_relacional expresion
                | empty
    '''


def p_op_relacional(p):
    '''
    op_relacional :  '>'
                | '<'
                | DEQUAL
                | LESSEQUAL
                | MOREEQUAL
                | DIFF
                | AND
                | OR
    '''
    #codigoExpAccion8
    if p[1] != None:
        pOper.append(p[1])

def p_exp(p):
    '''
    exp : termino codigoExpAccion4 exp1
    '''

def p_codigoExpAccion4(p):
    '''
    codigoExpAccion4 :
    '''
    if len(pOper) > 0:
        if pOper[len(pOper)-1] == '+' or pOper[len(pOper)-1] == '-' or pOper[len(pOper)-1] == 'or':
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            tipoSCube = scube.semantic_cube[tipoOp1][tipoOp2][operador]
            if tipoSCube > 0:
                operando2 = pilaO.pop()
                operando1 = pilaO.pop()
                global contTemp
                resultado = func_memTemp.generarEspacioMemoria(numToTipo[tipoSCube])
                nuevoCuad = [operador, operando1, operando2, resultado]
                global contCuadruplos
                contCuadruplos += 1
                global cuadruplos
                cuadruplos.append(nuevoCuad)
                #regresar temp al avail si se desocupo
                pilaO.append(resultado)
                pTipos.append(numToTipo[scube.semantic_cube[tipoOp1][tipoOp2][operador]])

            else:
                print("ERROR: operacion " + operador + " con tipos incompatibles.")
                sys.exit()

def p_exp1(p):
    '''
    exp1 : op_sum_res exp
            | empty
    '''

def p_op_sum_res(p):
    '''
    op_sum_res : '+'
                | '-'
                | OR
    '''
    #codigoExpAccion2
    if p[1] != None:
        pOper.append(p[1])

def p_termino(p):
    '''
    termino : exponente codigoExpAccion5 termino1
    '''

def p_codigoExpAccion5(p):
    '''
    codigoExpAccion5 :
    '''
    if len(pOper) > 0:
        if pOper[len(pOper)-1] == '*' or pOper[len(pOper)-1] == '/' or pOper[len(pOper)-1] == 'and':
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            tipoSCube = scube.semantic_cube[tipoOp1][tipoOp2][operador]
            if tipoSCube > 0:
                operando2 = pilaO.pop()
                operando1 = pilaO.pop()
                global contTemp
                resultado = func_memTemp.generarEspacioMemoria(numToTipo[tipoSCube])
                nuevoCuad = [operador, operando1, operando2, resultado]
                global contCuadruplos
                contCuadruplos += 1
                global cuadruplos
                cuadruplos.append(nuevoCuad)
                #regresar temp al avail si se desocupo
                pilaO.append(resultado)
                pTipos.append(numToTipo[scube.semantic_cube[tipoOp1][tipoOp2][operador]])

            else:
                print("ERROR: operacion " + operador + " con tipos incompatibles.")
                sys.exit()

def p_termino1(p):
    '''
    termino1 : op_mult_div termino
                | empty
    '''

def p_op_mult_div(p):
    '''
    op_mult_div : '*'
                | '/'
                | AND
    '''
    #codigoExpAccion3
    if p[1] != None:
        pOper.append(p[1])

def p_exponente(p):
    '''
    exponente : factor codigoExpAccion5_5 exponente1
    '''

def p_codigoExpAccion5_5(p):
    '''
    codigoExpAccion5_5 :
    '''
    if len(pOper) > 0:
        if pOper[len(pOper)-1] == '^':
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            tipoSCube = scube.semantic_cube[tipoOp1][tipoOp2][operador]
            if tipoSCube > 0:
                operando2 = pilaO.pop()
                operando1 = pilaO.pop()
                global contTemp
                resultado = func_memTemp.generarEspacioMemoria(numToTipo[tipoSCube])
                nuevoCuad = [operador, operando1, operando2, resultado]
                global contCuadruplos
                contCuadruplos += 1
                global cuadruplos
                cuadruplos.append(nuevoCuad)
                #regresar temp al avail si se desocupo
                pilaO.append(resultado)
                pTipos.append(numToTipo[scube.semantic_cube[tipoOp1][tipoOp2][operador]])

            else:
                print("ERROR: operacion " + operador + " con tipos incompatibles.")
                sys.exit()

def p_exponente1(p):
    '''
    exponente1 : op_exp exponente
                | empty
    '''
def p_op_exp(p):
    '''
    op_exp : '^'
    '''
    #codigoExpAccion5_5
    if p[1] != None:
        pOper.append(p[1])

def p_factor(p):
    '''
    factor : '(' inicio_parentesis expresion fin_parentesis ')'
            | constants
            | codigoExpAccion1
    '''

def p_inicio_parentesis(p):
    '''
    inicio_parentesis :
    '''
    #codigoExpAccion6
    pOper.append('(')

def p_fin_parentesis(p):
    '''
    fin_parentesis :
    '''
    #codigoExpAccion7
    pOper.pop()

def p_factor1(p):
    '''
    factor1 : asignacion_accion1 asignacion2
            | accion_llamadaProc1 factor2 ')' accion_llamadaProc5
            | ID
    '''
    if(len(p)<3):
        if p[1] in procs[current_scope][2].keys():
            variable = procs[current_scope][2][p[1]][0]
            tipo = variable
            tipo = tipo/10000
            tipo = tipo % 5
            tipo = numToTipo[tipo]
            pilaO.append(variable)
        elif p[1] in procs['global'].keys():
            variable = procs['global'][p[1]][0]
            tipo = variable
            tipo = tipo/10000
            tipo = numToTipo[tipo]
            pilaO.append(variable)
        else:
            print procs
            print p[1]
            print("ERROR: variable no declarada in %d" % lineNumber)
            sys.exit()
        pTipos.append(tipo)

def p_accion_llamadaProc1(p):
    '''
    accion_llamadaProc1 : ID '('
    '''
    if p[1] not in procs:
        print 'ERROR: Llamada a una funcion inexistente en linea %d.' % lineNumber
        sys.exit()
    else:
        nuevoCuadruplo = ['ERA', p[1], None, None]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1

        global contParametros
        contParametros.append(0)
        scopeParametros.append(p[1])

def p_factor2(p):
    '''
    factor2 : exp accion_llamadaProc3 factor3
            | empty
    '''

def p_accion_llamadaProc3(p):
    '''
    accion_llamadaProc3 :
    '''
    argumento = pilaO.pop()
    tipoArg = pTipos.pop()
    if tipoArg != procs[scopeParametros[-1]][1][contParametros[-1]]:
        print 'ERROR: Type mismatch in line %d.' % lineNumber
        sys.exit()
    else:
        nuevoCuadruplo = ['PARAM', argumento, None, contParametros[-1]]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1

def p_factor3(p):
    '''
    factor3 : ',' accion_llamadaProc4 exp accion_llamadaProc3 factor3
            | empty
    '''

def p_accion_llamadaProc4(p):
    '''
    accion_llamadaProc4 :
    '''
    contParametros[-1] += 1

def p_accion_llamadaProc5(p):
    '''
    accion_llamadaProc5 :
    '''
    scope = scopeParametros.pop()
    parametros = contParametros.pop()
    if len(procs[scope][1]) != parametros+1:
        print 'ERROR: Incongruencia de numero de parametros de la funcion en linea %d.' % lineNumber
        sys.exit()
    else:
        nuevoCuadruplo = ['GOSUB', scope, None, procs[scope][3]]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1

        #Parche guadalupano
        if scope in procs['global']:
            temp = func_memTemp.generarEspacioMemoria(procs[scope][0])
            dirScope = procs['global'][scope][0]
            nuevoCuadruplo2 = ['=', dirScope, None, temp]
            cuadruplos.append(nuevoCuadruplo2)
            contCuadruplos += 1
            pilaO.append(temp)
            pTipos.append(numToTipo[dirScope/10000])

def p_codigoExpAccion1(p):
    '''
    codigoExpAccion1 : factor1
    '''

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(p):
    global lineNumber
    print('Syntax error at token "%s" in line #%d.' % (p.value, lineNumber))
    sys.exit()

parser = yacc.yacc()

if len(sys.argv) < 2:
    fileName = raw_input('Archivo de entrada: ')
else:
    fileName = sys.argv[1]

with open(fileName) as codeFile:
    parser.parse(codeFile.read())

for cuadruplo in cuadruplos:
    print(cuadruplo)
