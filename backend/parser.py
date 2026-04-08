"""
Mini-C Compiler Parser
Parses tokens into an AST using PLY YACC
With improved error messages and comprehensive error recovery
"""

import ply.yacc as yacc
from lexer import tokens, Lexer

# Store parsing errors and context
parse_errors = []
current_code_lines = []
error_lines_reported = set()  # Track lines where errors were reported to avoid duplicates
parser_instance = None  # Global parser reference for error recovery


def get_line_content(lineno):
    """Get the content of a specific line for error context"""
    if 0 < lineno <= len(current_code_lines):
        return current_code_lines[lineno - 1].strip()
    return ""


def add_error(line, error_type, message):
    """Add an error if not already reported for this line with similar message"""
    global parse_errors, error_lines_reported
    # Create a key to avoid duplicate errors
    key = (line, message[:30])
    if key not in error_lines_reported:
        error_lines_reported.add(key)
        parse_errors.append({
            'line': line,
            'type': error_type,
            'message': message
        })


# AST Node classes
class ASTNode:
    """Base class for AST nodes"""
    pass


class Program(ASTNode):
    """Root node containing list of statements"""
    def __init__(self, statements):
        self.statements = statements if statements else []
    
    def __repr__(self):
        return f"Program({self.statements})"


class Declaration(ASTNode):
    """Variable declaration: int x; or int x = 5;"""
    def __init__(self, name, value=None, line=0):
        self.name = name
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Declaration({self.name}, {self.value})"


class Assignment(ASTNode):
    """Assignment: x = expr;"""
    def __init__(self, name, value, line=0):
        self.name = name
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Assignment({self.name}, {self.value})"


class BinaryOp(ASTNode):
    """Binary operation: expr op expr"""
    def __init__(self, op, left, right, line=0):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
    
    def __repr__(self):
        return f"BinaryOp({self.op}, {self.left}, {self.right})"


class Number(ASTNode):
    """Number literal"""
    def __init__(self, value, line=0):
        self.value = value
        self.line = line
    
    def __repr__(self):
        return f"Number({self.value})"


class Identifier(ASTNode):
    """Variable reference"""
    def __init__(self, name, line=0):
        self.name = name
        self.line = line
    
    def __repr__(self):
        return f"Identifier({self.name})"


class Printf(ASTNode):
    """Printf statement: printf("%d", x); or printf("%d %d", x, y);"""
    def __init__(self, format_string, args, line=0):
        self.format_string = format_string  # The format string like "%d"
        self.args = args  # List of expressions
        self.line = line
    
    def __repr__(self):
        return f"Printf({self.format_string}, {self.args})"


class IfStatement(ASTNode):
    """If statement: if (condition) { statements }"""
    def __init__(self, condition, body, line=0):
        self.condition = condition
        self.body = body
        self.line = line
    
    def __repr__(self):
        return f"If({self.condition}, {self.body})"


class Comparison(ASTNode):
    """Comparison: expr comp_op expr"""
    def __init__(self, op, left, right, line=0):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
    
    def __repr__(self):
        return f"Comparison({self.op}, {self.left}, {self.right})"


# Operator precedence (lowest to highest)
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)


# Grammar rules
def p_program(p):
    '''program : statement_list'''
    p[0] = Program(p[1])


def p_program_empty(p):
    '''program : '''
    p[0] = Program([])


def p_statement_list(p):
    '''statement_list : statement_list statement
                      | statement'''
    if len(p) == 3:
        # Filter out None statements (from error recovery)
        if p[2] is not None:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = p[1]
    else:
        # Single statement
        if p[1] is not None:
            p[0] = [p[1]]
        else:
            p[0] = []


def p_statement(p):
    '''statement : declaration
                 | assignment
                 | printf_stmt
                 | if_stmt'''
    p[0] = p[1]


# ============================================================
# ERROR RECOVERY RULES - Allow parser to continue after errors
# ============================================================

def p_statement_error_semi(p):
    '''statement : error SEMI'''
    # Recover at semicolon - skip the bad statement and continue
    p[0] = None


def p_statement_error_rbrace(p):
    '''statement : error RBRACE'''
    # Recover at closing brace - for malformed blocks
    p[0] = None


def p_declaration(p):
    '''declaration : INT ID SEMI
                   | INT ID ASSIGN expression SEMI'''
    if len(p) == 4:
        p[0] = Declaration(p[2], line=p.lineno(1))
    else:
        p[0] = Declaration(p[2], p[4], line=p.lineno(1))


def p_declaration_error_no_semi(p):
    '''declaration : INT ID ASSIGN expression'''
    add_error(p.lineno(4), 'Syntax', "Missing semicolon ';' at end of declaration")
    p[0] = Declaration(p[2], p[4], line=p.lineno(1))


def p_declaration_error_no_semi_simple(p):
    '''declaration : INT ID'''
    add_error(p.lineno(2), 'Syntax', "Missing semicolon ';' at end of declaration")
    p[0] = Declaration(p[2], line=p.lineno(1))


# Additional declaration error patterns
def p_declaration_error_missing_id(p):
    '''declaration : INT ASSIGN expression SEMI'''
    add_error(p.lineno(1), 'Syntax', "Missing variable name in declaration. Expected: int <name> = value;")
    p[0] = None


def p_declaration_error_missing_id_no_semi(p):
    '''declaration : INT ASSIGN expression'''
    add_error(p.lineno(1), 'Syntax', "Missing variable name in declaration. Expected: int <name> = value;")
    p[0] = None


def p_declaration_error_missing_value(p):
    '''declaration : INT ID ASSIGN SEMI'''
    add_error(p.lineno(3), 'Syntax', "Missing value after '=' in declaration")
    p[0] = Declaration(p[2], Number(0, p.lineno(3)), line=p.lineno(1))


def p_assignment(p):
    '''assignment : ID ASSIGN expression SEMI'''
    p[0] = Assignment(p[1], p[3], line=p.lineno(1))


def p_assignment_error_no_semi(p):
    '''assignment : ID ASSIGN expression'''
    add_error(p.lineno(3), 'Syntax', "Missing semicolon ';' at end of assignment")
    p[0] = Assignment(p[1], p[3], line=p.lineno(1))


# Additional assignment error patterns
def p_assignment_error_missing_value(p):
    '''assignment : ID ASSIGN SEMI'''
    add_error(p.lineno(2), 'Syntax', "Missing value after '=' in assignment")
    p[0] = None


def p_assignment_error_missing_expr(p):
    '''assignment : ID ASSIGN error SEMI'''
    add_error(p.lineno(2), 'Syntax', "Invalid expression after '=' in assignment")
    p[0] = None


# Printf with format string and arguments
def p_printf_stmt_format(p):
    '''printf_stmt : PRINTF LPAREN STRING COMMA arg_list RPAREN SEMI'''
    p[0] = Printf(p[3], p[5], line=p.lineno(1))


def p_printf_stmt_format_only(p):
    '''printf_stmt : PRINTF LPAREN STRING RPAREN SEMI'''
    p[0] = Printf(p[3], [], line=p.lineno(1))


# Printf with just expression (backward compatibility)
def p_printf_stmt_expr(p):
    '''printf_stmt : PRINTF LPAREN expression RPAREN SEMI'''
    p[0] = Printf(None, [p[3]], line=p.lineno(1))


def p_printf_stmt_error_no_semi(p):
    '''printf_stmt : PRINTF LPAREN STRING COMMA arg_list RPAREN
                   | PRINTF LPAREN STRING RPAREN
                   | PRINTF LPAREN expression RPAREN'''
    add_error(p.lineno(1), 'Syntax', "Missing semicolon ';' at end of printf statement")
    if len(p) == 7:
        p[0] = Printf(p[3], p[5], line=p.lineno(1))
    elif len(p) == 5 and isinstance(p[3], str) and p[3].startswith('"'):
        p[0] = Printf(p[3], [], line=p.lineno(1))
    else:
        p[0] = Printf(None, [p[3]], line=p.lineno(1))


# Additional printf error patterns
def p_printf_stmt_error_missing_paren(p):
    '''printf_stmt : PRINTF LPAREN STRING COMMA arg_list SEMI
                   | PRINTF LPAREN STRING SEMI
                   | PRINTF LPAREN expression SEMI'''
    add_error(p.lineno(1), 'Syntax', "Missing closing parenthesis ')' in printf statement")
    if len(p) == 7:
        p[0] = Printf(p[3], p[5], line=p.lineno(1))
    elif len(p) == 5 and isinstance(p[3], str) and p[3].startswith('"'):
        p[0] = Printf(p[3], [], line=p.lineno(1))
    else:
        p[0] = Printf(None, [p[3]], line=p.lineno(1))


def p_printf_stmt_error_missing_lparen(p):
    '''printf_stmt : PRINTF STRING RPAREN SEMI'''
    add_error(p.lineno(1), 'Syntax', "Missing opening parenthesis '(' in printf statement")
    p[0] = Printf(p[2], [], line=p.lineno(1))


def p_printf_stmt_error_no_args(p):
    '''printf_stmt : PRINTF LPAREN RPAREN SEMI'''
    add_error(p.lineno(1), 'Syntax', "printf requires at least a format string or expression")
    p[0] = None


def p_arg_list(p):
    '''arg_list : arg_list COMMA expression
               | expression'''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_if_stmt(p):
    '''if_stmt : IF LPAREN condition RPAREN LBRACE statement_list RBRACE'''
    p[0] = IfStatement(p[3], p[6], line=p.lineno(1))


def p_if_stmt_empty_body(p):
    '''if_stmt : IF LPAREN condition RPAREN LBRACE RBRACE'''
    p[0] = IfStatement(p[3], [], line=p.lineno(1))


def p_if_stmt_error_no_brace(p):
    '''if_stmt : IF LPAREN condition RPAREN statement'''
    add_error(p.lineno(1), 'Syntax', "Missing braces '{ }' around if statement body")
    p[0] = IfStatement(p[3], [p[5]], line=p.lineno(1))


# Additional if statement error patterns
def p_if_stmt_error_no_lparen(p):
    '''if_stmt : IF condition RPAREN LBRACE statement_list RBRACE'''
    add_error(p.lineno(1), 'Syntax', "Missing opening parenthesis '(' after 'if'")
    p[0] = IfStatement(p[2], p[5], line=p.lineno(1))


def p_if_stmt_error_no_rparen(p):
    '''if_stmt : IF LPAREN condition LBRACE statement_list RBRACE'''
    add_error(p.lineno(1), 'Syntax', "Missing closing parenthesis ')' after condition")
    p[0] = IfStatement(p[3], p[5], line=p.lineno(1))


def p_if_stmt_error_no_condition(p):
    '''if_stmt : IF LPAREN RPAREN LBRACE statement_list RBRACE'''
    add_error(p.lineno(1), 'Syntax', "Missing condition in if statement")
    p[0] = None


def p_if_stmt_error_missing_lbrace(p):
    '''if_stmt : IF LPAREN condition RPAREN statement_list RBRACE'''
    add_error(p.lineno(1), 'Syntax', "Missing opening brace '{' for if statement body")
    p[0] = IfStatement(p[3], p[5], line=p.lineno(1))


def p_if_stmt_error_missing_rbrace(p):
    '''if_stmt : IF LPAREN condition RPAREN LBRACE statement_list'''
    add_error(p.lineno(1), 'Syntax', "Missing closing brace '}' for if statement body")
    p[0] = IfStatement(p[3], p[6], line=p.lineno(1))


def p_condition(p):
    '''condition : expression comparison_op expression'''
    p[0] = Comparison(p[2], p[1], p[3], line=p.lineno(2))


def p_comparison_op(p):
    '''comparison_op : LT
                     | GT
                     | LE
                     | GE
                     | EQ
                     | NE'''
    p[0] = p[1]


def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    p[0] = BinaryOp(p[2], p[1], p[3], line=p.lineno(2))


def p_expression_group(p):
    '''expression : LPAREN expression RPAREN'''
    p[0] = p[2]


def p_expression_number(p):
    '''expression : NUMBER'''
    p[0] = Number(p[1], line=p.lineno(1))


def p_expression_id(p):
    '''expression : ID'''
    p[0] = Identifier(p[1], line=p.lineno(1))


def p_error(p):
    """Syntax error handler with improved messages and error recovery"""
    global parse_errors, parser_instance
    
    if p:
        line = p.lineno
        value = p.value
        
        # Provide context-aware error messages
        if p.type == 'ID':
            # Check common mistakes
            if value in ('for', 'while', 'do'):
                message = f"Loops ('{value}') are not supported in Mini-C"
            elif value in ('else', 'switch', 'case'):
                message = f"'{value}' statements are not supported in Mini-C"
            elif value in ('return'):
                message = "Return statements are not supported in Mini-C"
            elif value in ('char', 'float', 'double', 'void'):
                message = f"Type '{value}' is not supported. Only 'int' is allowed in Mini-C"
            elif value in ('main'):
                message = "Function definitions are not supported in Mini-C. Write statements directly without main()"
            else:
                message = f"Unexpected identifier '{value}'"
        elif p.type == 'NUMBER':
            message = f"Unexpected number '{value}'. Check for missing operator or semicolon"
        elif p.type == 'SEMI':
            message = "Unexpected semicolon. Check for empty statement or extra semicolon"
        elif p.type == 'LBRACE':
            message = "Unexpected '{'. Braces should only be used with if statements"
        elif p.type == 'RBRACE':
            message = "Unexpected '}'. Check for missing opening brace or extra closing brace"
        elif p.type == 'LPAREN':
            message = "Unexpected '('. Parentheses should be used with if conditions or printf"
        elif p.type == 'RPAREN':
            message = "Unexpected ')'. Check for missing opening parenthesis"
        elif p.type in ('PLUS', 'MINUS', 'TIMES', 'DIVIDE'):
            message = f"Unexpected operator '{value}'. Check for missing operand"
        elif p.type == 'ASSIGN':
            message = "Unexpected '='. Check for missing variable name or use '==' for comparison"
        elif p.type in ('LT', 'GT', 'LE', 'GE', 'EQ', 'NE'):
            message = f"Unexpected comparison operator '{value}'. Comparisons should be inside if conditions"
        elif p.type == 'INT':
            message = "Unexpected 'int'. Check for missing semicolon in previous statement"
        elif p.type == 'IF':
            message = "Unexpected 'if'. Check for missing semicolon in previous statement"
        elif p.type == 'PRINTF':
            message = "Unexpected 'printf'. Check for missing semicolon in previous statement"
        elif p.type == 'STRING':
            message = f"Unexpected string {value}. Strings should only be used in printf format"
        elif p.type == 'COMMA':
            message = "Unexpected comma. Commas should only be used to separate printf arguments"
        else:
            message = f"Unexpected token '{value}'"
        
        add_error(line, 'Syntax', message)
        
        # Error recovery: find synchronization point and continue parsing
        if parser_instance:
            # Tell parser to reset error state so it can continue
            parser_instance.errok()
    else:
        # Unexpected end of input
        line = len(current_code_lines) if current_code_lines else 1
        add_error(line, 'Syntax', 
                  "Unexpected end of input. Check for missing semicolon, closing brace, or incomplete statement")


class Parser:
    """Wrapper class for the PLY parser with comprehensive error recovery"""
    
    def __init__(self):
        global parser_instance
        self.lexer = Lexer()
        self.parser = yacc.yacc(debug=False, write_tables=False)
        parser_instance = self.parser
    
    def parse(self, code):
        """
        Parse the input code and return AST and errors
        
        Args:
            code: String containing Mini-C source code
            
        Returns:
            tuple: (AST, list of errors)
        """
        global parse_errors, current_code_lines, error_lines_reported, parser_instance
        parse_errors = []
        error_lines_reported = set()
        current_code_lines = code.split('\n')
        parser_instance = self.parser
        
        # Get lexer and check for lexical errors first
        lex = self.lexer.get_lexer()
        lex.input(code)
        
        # Collect all tokens to check for lexical errors
        tokens_collected = []
        while True:
            tok = lex.token()
            if not tok:
                break
            tokens_collected.append(tok)
        
        # Get lexer errors
        lexer_errors = list(self.lexer.lexer.errors)
        
        # Reset and get fresh lexer for parser
        lex = self.lexer.get_lexer()
        
        # Parse the code
        try:
            ast = self.parser.parse(code, lexer=lex, tracking=True)
        except Exception as e:
            add_error(1, 'Syntax', f"Parser error: {str(e)}")
            ast = None
        
        # Combine lexer and parser errors
        all_errors = lexer_errors + parse_errors
        
        # Sort errors by line number (chronological order)
        all_errors.sort(key=lambda x: x['line'])
        
        # Remove duplicate errors
        seen = set()
        unique_errors = []
        for err in all_errors:
            key = (err['line'], err['type'], err['message'][:50])
            if key not in seen:
                seen.add(key)
                unique_errors.append(err)
        
        return ast, unique_errors


# For testing
if __name__ == "__main__":
    test_cases = [
        # Valid code
        """
        int x;
        int y = 10;
        x = 5;
        x = x + y * 2;
        if (x > 3) {
            printf("%d", x);
        }
        printf("%d %d", x, y);
        """,
        # Missing semicolon
        """
        int x = 5
        printf("%d", x);
        """,
        # Using unsupported loop
        """
        int x = 5;
        for (int i = 0; i < 10; i++) {
            printf("%d", i);
        }
        """,
    ]
    
    parser = Parser()
    
    for i, code in enumerate(test_cases):
        print(f"\n=== Test Case {i + 1} ===")
        print(f"Code: {code.strip()[:50]}...")
        ast, errors = parser.parse(code)
        
        if errors:
            print("Errors:")
            for err in errors:
                print(f"  Line {err['line']}: [{err['type']}] {err['message']}")
        else:
            print("Parse successful!")
            print(f"AST: {ast}")
