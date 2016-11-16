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
    'add' : 'ADD',
    'get' : 'GET',
    'remove' : 'REMOVE',
    'modify' : 'MODIFY',
    'load' : 'LOAD',
    'size' : 'SIZE',
    'main' : 'MAIN',
    'AND' : 'AND',
    'OR' : 'OR',
    'return' : 'RETURN'
}

#Tokens
tokens = [
    'ID',
    'CTE_INT',
    'CTE_FLOAT',
    'CTE_STR',
    'CTE_CHAR',
    'CTE_BOOL',
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
t_CTE_BOOL = r'True|False'
t_LESSEQUAL = r'<='
t_MOREEQUAL = r'>='
t_DEQUAL = r'=='
t_DIFF = r'<>'

literals = ";:,\{\}\<\>\+\-\*\/\(\)="

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
    global procs
    print(procs)
    global constantes
    print constantes

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
    print(p[1])
    global procs
    if current_scope == 'global':
        if p[2] in procs[current_scope].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            procs[current_scope][p[2]]=memGlobales.generarEspacioMemoria(p[1])

    else:
        print procs
        if p[2] in procs['global'].keys() or p[2] in procs[current_scope][2].keys():
            print("ERROR: variable con el mismo nombre declarada dos veces en linea %d." % lineNumber)
            sys.exit()
        else:
            global inParams
            if inParams:
                procs[current_scope][1].append(p[1])
            procs[current_scope][2][p[2]] = func_memLocal.generarEspacioMemoria(p[1])

def p_initialize_var(p):
    '''
    initialize_var : '=' expresion
                    | empty
    '''

def p_vector(p):
    '''
    vector : VEC tipo ID
    '''

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
    cte_bool : CTE_BOOL
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
    current_scope = 'global'
    #creo que hay que marcar end aqui

def p_t_main(p):
    '''
    t_main : MAIN
    '''
    scope = p[1]
    if scope in procs:
        print('ERROR: Funcion repetida en linea %d.' % lineNumber)
        sys.exit()
    global current_scope
    current_scope = scope
    global func_memLocal, func_memTemp
    func_memLocal = mem.Memoria(inicioLocal)
    func_memTemp = mem.Memoria(inicioTemp)
    global procs
    procs[current_scope] = [p[1], [], {}, contCuadruplos]

def p_funciones(p):
    '''
    funciones : t_new_func '(' t_inParams params t_outParams ')' '{' declare_vars inicio_cuadruplo estatuto return_body '}' end_func funciones
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

def p_t_new_func(p):
    '''
    t_new_func : func_tipo ID
    '''
    scope = p[2]
    if scope in procs:
        print('ERROR: Funcion repetida en linea %d.' % lineNumber)
        sys.exit()
    global current_scope
    current_scope = scope
    global func_memLocal, func_memTemp
    func_memLocal = mem.Memoria(inicioLocal)
    func_memTemp = mem.Memoria(inicioTemp)
    global procs
    procs[current_scope] = [p[1], [], {}, contCuadruplos]
    #Crear una variable para el valor de retorno de la funcion
    if p[2] in procs['global'].keys():
        print("ERROR: variable/funcion con el mismo nombre declarada dos veces en linea %d." % lineNumber)
        sys.exit()
    else:
        if p[1] != 'VOID':
            procs['global'][p[2]] = memGlobales.generarEspacioMemoria(p[1])

def p_func_tipo(p):
    '''
    func_tipo : tipo
                | VOID
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
                | empty
    '''

def p_return_accion1(p):
    '''
    return_accion1 :
    '''
    valorRetorno = pilaO.pop()
    tipoRetorno = pTipos.pop()
    tipoFunc = procs[current_scope][0]
    if scube.semantic_cube[tipoFunc][tipoRetorno]['=']:
        nuevoCuadruplo = ['=', valorRetorno, None, current_scope]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1

        nuevoCuadruplo = ['RETURN', valorRetorno, None, current_scope]
        cuadruplos.append(nuevoCuadruplo)
        contCuadruplos += 1

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
                | graficar
                | op_vector
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
        tipo = procs[current_scope][2][p[1]]
        tipo = tipo/10000
        tipo = tipo % 5
        tipo = numToTipo[tipo]
        pilaO.append(procs[current_scope][2][p[1]])
    elif p[1] in procs['global'].keys():
        tipo = procs['global'][p[1]]
        tipo = tipo/10000
        tipo = numToTipo[tipo]
        pilaO.append(procs[current_scope][p[1]])
    pTipos.append(tipo)

def p_asignacion_accion2(p):
    '''
    asignacion_accion2 : '='
    '''
    pOper.append(p[1])

def p_asignacion2(p):
    '''
    asignacion2 : '[' exp ']'
                | empty
    '''

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
    print("saltos before if aux rep accion 2")
    print(pSaltos)
    print pTipos
    print pOper
    print pilaO
    aux = pTipos.pop()
    if aux != 'BOOL':
        print('ERROR: Type mismatch in %d.' % lineNumber)
        sys.exit()
    else:
        print("saltos else")
        print(pSaltos)
        resultado = pilaO.pop()
        #Generar cuadruplo
        cuadruplos.append(['GOTOF', resultado, None, None])
        global contCuadruplos
        contCuadruplos += 1

        print("saltos before")
        print(pSaltos)
        pSaltos.append(contCuadruplos - 1)
        print("saltos after")
        print(pSaltos)

def p_repeticion_accion3(p):
    '''
    repeticion_accion3 :
    '''
    print("saltos ")
    print(pSaltos)
    falso = pSaltos.pop()
    print("saltos ")
    print(pSaltos)
    retorno = pSaltos.pop()

    cuadruplos.append(['GOTO', None, None, retorno])
    global contCuadruplos
    contCuadruplos += 1

    cuadruplos[falso][3] = contCuadruplos

def p_escritura(p):
    '''
    escritura : PRINT '(' escritura1 ')' ';'
    '''
    resultado = pilaO.pop()
    nuevoCuadruplo = [p[1], resultado, None, None]
    cuadruplos.append(nuevoCuadruplo)
    global contCuadruplos
    contCuadruplos += 1

def p_escritura1(p):
    '''
    escritura1 : expresion
    '''

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

def p_op_vector(p):
    '''
    op_vector : ID '.' op_vector1 ')'
    '''

def p_op_vector1(p):
    '''
    op_vector1 : op_vector2 exp
                | LOAD '(' CTE_STR
                | SIZE '('
    '''

def p_op_vector2(p):
    '''
    op_vector2 : op_vector3
                | MODIFY '(' exp ','
    '''

def p_op_vector3(p):
    '''
    op_vector3 : ADD '('
                | GET '('
                | REMOVE '('
    '''

def p_expresion(p):
    '''
    expresion : exp codigoExpAccion9 expresion1
    '''

def p_codigoExpAccion9(p):
    '''
    codigoExpAccion9 :
    '''
    print "codgo accion 9"
    print(len(pOper))
    print pilaO
    print pOper
    if len(pOper) > 0:
        print "inside first if cea9"
        print pOper
        print pilaO
        print pOper[len(pOper)-1]
        if (pOper[len(pOper)-1] == '>' or pOper[len(pOper)-1] == '<' or
            pOper[len(pOper)-1] == '>=' or pOper[len(pOper)-1] == '=>' or
            pOper[len(pOper)-1] == '==' or pOper[len(pOper)-1] == '<>'):
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            print "adios 1"
            print tipoOp1
            print tipoOp2
            print operador
            tipoSCube = scube.semantic_cube[tipoOp1][tipoOp2][operador]
            if tipoSCube > 0:
                print "adios 2"
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
        print "poper before append op rel"
        print pOper
        pOper.append(p[1])
        print "pOper after append op rel"
        print pOper

def p_exp(p):
    '''
    exp : termino codigoExpAccion4 exp1
    '''

def p_codigoExpAccion4(p):
    '''
    codigoExpAccion4 :
    '''
    if len(pOper) > 0:
        if pOper[len(pOper)-1] == '+' or pOper[len(pOper)-1] == '-':
            operador = pOper.pop()
            tipoOp2 = pTipos.pop()
            tipoOp1 = pTipos.pop()
            print tipoOp1, tipoOp2
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
        if pOper[len(pOper)-1] == '*' or pOper[len(pOper)-1] == '/':
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
            | codigoExpAccion1
            | constants
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
    factor1 : ID '[' exp ']'
            | accion_llamadaProc1 factor2 ')' accion_llamadaProc5
            | ID
    '''
    if(len(p)<3):
        tipo = ""
        if p[1] in procs[current_scope][2].keys():
            tipo = procs[current_scope][2][p[1]]
            tipo = tipo/10000
            tipo = tipo % 5
            tipo = numToTipo[tipo]
            pilaO.append(procs[current_scope][2][p[1]])
        elif p[1] in procs['global'].keys():
            tipo = procs['global'][p[1]]
            tipo = tipo/10000
            tipo = numToTipo[tipo]
            pilaO.append(procs[current_scope][p[1]])

        else:
            print("ERROR: variable no declarada")
            sys.exit()
        print "TIPO BEF APPEND"
        print tipo
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
        nuevoCuadruplo = ['GOSUB', scope, procs[scope][3]]
        cuadruplos.append(nuevoCuadruplo)
        global contCuadruplos
        contCuadruplos += 1

        #Parche guadalupano
        if scope in procs['global']:
            temp = func_memTemp.generarEspacioMemoria(procs[scope][0])
            nuevoCuadruplo2 = ['=', scope, None, temp]
            cuadruplos.append(nuevoCuadruplo2)
            contCuadruplos += 1
            pilaO.append(temp)
            pTipos.append(numToTipo[procs['global'][scope]/10000])

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
