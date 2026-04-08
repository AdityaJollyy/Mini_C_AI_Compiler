"""
Mini-C Compiler Lexer
Tokenizes a subset of C language using PLY (Python Lex-Yacc)
"""

import ply.lex as lex

# List of token names
tokens = (
    # Keywords
    'INT',
    'IF',
    'PRINTF',
    
    # Identifiers and literals
    'ID',
    'NUMBER',
    'STRING',
    
    # Operators
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'ASSIGN',
    
    # Comparison operators
    'LT',
    'GT',
    'LE',
    'GE',
    'EQ',
    'NE',
    
    # Delimiters
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMI',
    'COMMA',
)

# Reserved words mapping
reserved = {
    'int': 'INT',
    'if': 'IF',
    'printf': 'PRINTF',
}

# Simple token rules (single characters)
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_COMMA = r','

# Comparison operators (order matters - longer patterns first)
t_LE = r'<='
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'

# Ignored characters (spaces and tabs)
t_ignore = ' \t'


def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    # Keep the quotes for easier parsing
    t.value = t.value
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Check for reserved words
    t.type = reserved.get(t.value, 'ID')
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_COMMENT(t):
    r'//.*'
    pass  # Ignore single-line comments


def t_BLOCK_COMMENT(t):
    r'/\*[\s\S]*?\*/'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignore block comments


def t_error(t):
    """Error handling rule"""
    char = t.value[0]
    
    # Provide more helpful error messages
    if char == '"':
        message = "Unterminated string literal"
    elif char == "'":
        message = "Single quotes not supported. Use double quotes for strings"
    elif char in '[]':
        message = f"Arrays are not supported in Mini-C (found '{char}')"
    elif char == '&':
        message = "Pointers/address-of operator not supported in Mini-C"
    elif char == '#':
        message = "Preprocessor directives not supported in Mini-C"
    else:
        message = f"Illegal character '{char}'"
    
    error = {
        'line': t.lexer.lineno,
        'type': 'Lexical',
        'message': message
    }
    t.lexer.errors.append(error)
    t.lexer.skip(1)


class Lexer:
    """Wrapper class for the PLY lexer"""
    
    def __init__(self):
        self.lexer = lex.lex()
        self.lexer.errors = []
    
    def tokenize(self, code):
        """
        Tokenize the input code and return tokens and errors
        
        Args:
            code: String containing Mini-C source code
            
        Returns:
            tuple: (list of tokens, list of errors)
        """
        self.lexer.errors = []
        self.lexer.lineno = 1
        self.lexer.input(code)
        
        tokens_list = []
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            tokens_list.append({
                'type': tok.type,
                'value': tok.value,
                'line': tok.lineno,
            })
        
        return tokens_list, self.lexer.errors
    
    def get_lexer(self):
        """Return the raw PLY lexer for use with the parser"""
        self.lexer.errors = []
        self.lexer.lineno = 1
        return self.lexer


# For testing
if __name__ == "__main__":
    test_code = """
    int x;
    int y = 10;
    x = 5;
    if (x > 3) {
        printf("%d", x);
    }
    printf("%d %d", x, y);
    """
    
    lexer = Lexer()
    tokens, errors = lexer.tokenize(test_code)
    
    print("Tokens:")
    for tok in tokens:
        print(f"  {tok}")
    
    if errors:
        print("\nErrors:")
        for err in errors:
            print(f"  Line {err['line']}: {err['message']}")
