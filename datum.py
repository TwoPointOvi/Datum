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
    'size' : 'SIZE'
}

#Tokens
tokens = [
    'ID',
    'CTEI',
    'CTEF',
    'CTES',
    'CTEC',
    'CTEB',
    'LESSEQUAL',
    'MOREEQUAL',
    'DEQUAL'
]

t_CTEI = r'(\+|-)?[0-9]+'
t_CTEF = r'(\+|-)?[0-9]*\.[0-9]+'
t_CTES = r'\".*\"'
t_CTEC = r'\'.\''
t_CTEB = r'True|False'
t_LESSEQUAL = r'<='
t_MOREEQUAL = r'>='
t_DEQUAL = r'=='

tokens += list(reserved.values())

literals = ";:,\{\}\<\>\+\-\*\/\(\)="

t_ignore = " \t\n"

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

#Gramatica
def p_progam(p):
    '''
    program : ID ';' declare_vars prog_body
    '''

def p_declar_vars(p):
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
    prog_body : '{' funciones '}'
    '''

def p_funciones(p):
    '''
    funciones : func_tipo ID '(' params ')' '{' vars estatuto return_body '}'
    '''

def p_func_tipo(p):
    '''
    func_tipo : TIPO
                | VOID
    '''

def p_params(p):
    '''
    params : var
            | ',' var
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
    estatuto : asignacion
                | condicion
                | repeticion
                | escritura
                | graficar
                | op_vector
    '''

def p_asignacion(p):
    '''
    asignacion : ID asignacion2 '=' expresion ';'
                | '[' exp ']'
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
    repeticion : '(' expresion ')' bloque
    '''

def p_escritura(p):
    '''
    escritura : PRINT '(' escritura1 ')'
    '''

def p_escritura1(p):
    '''
    escritura1 : expresion
                | constants
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
    pie_chart : PIE_CHART '(' ID ',' ID ',' title ')'
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

def p_progam(p):
    '''
    '''







