import lex


class PythonLexer:
    """A Python lexer."""

    reserved = {
        'def': 'DEF'
    }

    tokens = [
                 'NUMBER',
                 'POWER',
                 'EUCLIDEAN_DIV',
                 'SPACE',
                 'ID',
             ] + list(reserved)

    states = (
        ('newline', 'inclusive'),
    )

    def t_begin_newline(self, t):
        r'\n'
        print("Entering newline state.")
        t.lexer.begin('newline')

    def t_newline_end(self, t):
        r'[^ ]'
        print("Exiting newline state.")
        t.lexer.begin('INITIAL')

    t_newline_SPACE = r'[ ]'

    t_POWER = r'[*]{2}'
    t_EUCLIDEAN_DIV = r'[/]{2}'

    t_ignore = ' '
    t_newline_ignore = ''

    literals = ['*', '/', '+', '-', '(', ')', ':', '=']

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = PythonLexer.reserved.get(t.value, 'ID')
        return t

    def t_error(self, t):
        print(f"Illegal character {t.value}")
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def test(self, data):
        self.lexer.input(data)

        while True:
            token = self.lexer.token()
            if not token:
                break
            print(token)


if __name__ == "__main__":
    lexer = PythonLexer()
    lexer.build()
    lexer.test('''def x(foo):
        x = 12''')
