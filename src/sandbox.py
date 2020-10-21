import lex

reserved = {
    'if': 'IF',
    'def': 'DEF',
    'class': 'class'
}

tokens = [
             'NUMBER'
             'PLUS',
             'MINUS',
             'TIMES',
             'DIVIDE',
             'LPAREN',
             'RPAREN',
             'COLONS',
             'ID'
         ] + list(reserved)

t_PLUS = r'[+]'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


t_ignore = ' '


def t_error(t):
    print("Illegal character '%s'" % t.value)
    t.lexer.skip(1)


lexer = lex.lex()
data = '''
1 + 2
'''
lexer.input(data)

while True:
    tok = lexer.token()
    if not tok:
        break
    print(tok)
