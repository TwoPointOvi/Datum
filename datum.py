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
t_CTEC = r'.'
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



