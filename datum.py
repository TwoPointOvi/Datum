import ply.lex as lex
import ply.yacc as yacc

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
    lineNumber += 1
    t.lexer.lineno += len(t.value)

def t_ID(t):
    r'(_*[a-zA-Z]+_*[0-9]*_*)+'
    #Check for reserved words
    t.type = reserved.get(t.value, 'ID')
    return t

def t_error(t):
    print("Caracter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

#Build lexer
lex.lex()


#Tabla Procedimiento
procs = {}

#Variable to save the current scope
current_scope = 'global'

#Gramatica
def p_progam(p):
    '''
    program : t_prog ID ';' declare_vars prog_body
    '''
    print(procs)

def p_t_prog(p):
    '''
    t_prog : PROGRAM
    '''
    procs['global'] = []

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
    if current_scope == 'global':
        procs[current_scope].append([p[2],p[1]])

def p_initialize_var(p):
    '''
    initialize_var : '=' constants
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
    constants : CTE_INT
            | CTE_FLOAT
            | CTE_STR
            | CTE_CHAR
            | CTE_BOOL
    '''

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

def p_t_main(p):
    '''
    t_main : MAIN
    '''
    global current_scope
    current_scope = 'main'

def p_funciones(p):
    '''
    funciones : t_new_func '(' params ')' '{' declare_vars estatuto return_body '}' funciones
                | empty
    '''
    global current_scope
    current_scope = 'global'

def p_t_new_func(p):
    '''
    t_new_func : func_tipo ID
    '''
    global current_scope
    current_scope = p[2]
    global procs
    procs[current_scope] = [p[1], [], []]

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
    return_body : RETURN expresion ';'
                | empty
    '''

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
    estatuto2 : estatuto1
                | empty
    '''

def p_asignacion(p):
    '''
    asignacion : ID asignacion2 '=' expresion ';'
    '''

def p_asignacion2(p):
    '''
    asignacion2 : '[' exp ']'
                | empty
    '''

def p_condicion(p):
    '''
    condicion : IF '(' expresion ')' bloque condicion1
    '''

def p_condicion1(p):
    '''
    condicion1 : ELSE bloque
                | empty
    '''

def p_repeticion(p):
    '''
    repeticion : WHILE '(' expresion ')' bloque
    '''

def p_escritura(p):
    '''
    escritura : PRINT '(' escritura1 ')' ';'
    '''

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
    expresion : exp expresion1
    '''

def p_expresion1(p):
    '''
    expresion1 : '>' expresion
                | '<' expresion
                | DEQUAL expresion
                | LESSEQUAL expresion
                | MOREEQUAL expresion
                | DIFF expresion
                | AND expresion
                | OR expresion
                | empty
    '''

def p_exp(p):
    '''
    exp : termino exp1
    '''

def p_exp1(p):
    '''
    exp1 : '+' exp
            | '-' exp
            | empty
    '''

def p_termino(p):
    '''
    termino : exponente termino1
    '''

def p_termino1(p):
    '''
    termino1 : '*' termino
                | '/' termino
                | empty
    '''

def p_exponente(p):
    '''
    exponente : factor exponente1
    '''

def p_exponente1(p):
    '''
    exponente1 : '^' exponente
                | empty
    '''

def p_factor(p):
    '''
    factor : '(' expresion ')'
            | ID factor1
            | constants
    '''

def p_factor1(p):
    '''
    factor1 : '[' exp ']'
            | '(' factor2 ')'
            | empty
    '''

def p_factor2(p):
    '''
    factor2 : exp factor3
            | empty
    '''

def p_factor3(p):
    '''
    factor3 : ',' exp factor2
            |
    '''

def p_empty(p):
    '''
    empty :
    '''
    pass

def p_error(p):
    global lineNumber
    print('Syntax error at token "%s" in line #%d.' % (p.value, lineNumber))

parser = yacc.yacc()

import sys
if len(sys.argv) < 2:
    fileName = raw_input('Archivo de entrada: ')
else:
    fileName = sys.argv[1]

with open(fileName) as codeFile:
    parser.parse(codeFile.read())
