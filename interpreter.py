(INT, ADD, SUB, MUL, DIV, LEFTBRAC, RIGHTBRAC, ALPHANUM, ASSIGNMENT,
 BEGIN, END, SEMICOLON, DOT, EOF) = (
    'INT', 'ADD', 'SUB', 'MUL', 'DIV', '(', ')', 'ALPHANUM', 'ASSIGNMENT',
    'BEGIN', 'END', 'SEMICOLON', 'DOT', 'EOF'
)


class Value_tokens(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return 'Value_tokens({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.str()


RESERVED_KEYWORDS = {
    'BEGIN': Value_tokens('BEGIN', 'BEGIN'),
    'END': Value_tokens('END', 'END'),
}


class Lexer(object):
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def invalid(self):
        raise Exception('Invalid character')

    def inc(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None 
        else:
            self.current_char = self.text[self.pos]

    def check(self):
        check_pos = self.pos + 1
        if check_pos > len(self.text) - 1:
            return None
        else:
            return self.text[check_pos]

    def skip_space(self):
        while self.current_char is not None and self.current_char.isspace():
            self.inc()

    def integer(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.inc()
        return int(result)

    def Reserved(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.inc()

        token = RESERVED_KEYWORDS.get(result, Value_tokens(ALPHANUM, result))
        return token

    def next_token(self):
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_space()
                continue

            if self.current_char.isalpha():
                return self.Reserved()

            if self.current_char.isdigit():
                return Value_tokens(INT, self.integer())

            if self.current_char == '=':
                self.inc()
                return Value_tokens(ASSIGNMENT, '=')

            if self.current_char == ';':
                self.inc()
                return Value_tokens(SEMICOLON, ';')

            if self.current_char == '+':
                self.inc()
                return Value_tokens(ADD, '+')

            if self.current_char == '-':
                self.inc()
                return Value_tokens(SUB, '-')

            if self.current_char == '*':
                self.inc()
                return Value_tokens(MUL, '*')

            if self.current_char == '/':
                self.inc()
                return Value_tokens(DIV, '/')

            if self.current_char == '(':
                self.inc()
                return Value_tokens(LEFTBRAC, '(')

            if self.current_char == ')':
                self.inc()
                return Value_tokens(RIGHTBRAC, ')')

            self.error()

        return Value_tokens(EOF, None)



class AST(object):
    pass


class Binary_operation(AST):
    def __init__(self, lop, oper, rop):
        self.left = lop
        self.token = self.op = oper
        self.right = rop


class int_value(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class operator_uneray(AST):
    def __init__(self, oper, exp):
        self.token = self.op = oper
        self.expr = exp


class begin_end(AST):
    def __init__(self):
        self.children = []


class Assignment(AST):
    def __init__(self, lop, oper, rop):
        self.left = lop
        self.token = self.op = oper
        self.right = rop


class Value_var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class No_Oper(AST):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def invalid(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.next_token()
        else:
            self.invalid()

    def code(self):
        node = self.beg_st_end()
        return node

    def beg_st_end(self):
        nodes = self.list_statements()

        root = begin_end()
        for node in nodes:
            root.children.append(node)

        return root

    def list_statements(self):
        node = self.stmt()

        results = [node]

        while self.current_token.type == SEMICOLON:
            self.eat(SEMICOLON)
            results.append(self.stmt())

        if self.current_token.type == ALPHANUM:
            self.invalid()

        return results

    def stmt(self):
        if self.current_token.type == ALPHANUM:
            node = self.variable_assign()
        else:
            node = self.empty()
        return node

    def variable_assign(self):
        left = self.var()
        token = self.current_token
        self.eat(ASSIGNMENT)
        right = self.expr()
        node = Assignment(left, token, right)
        return node

    def var(self):
        node = Value_var(self.current_token)
        self.eat(ALPHANUM)
        return node

    def empty(self):
        return No_Oper()

    def expr(self):
        node = self.trm()

        while self.current_token.type in (ADD, SUB):
            token = self.current_token
            if token.type == ADD:
                self.eat(ADD)
            elif token.type == SUB:
                self.eat(SUB)

            node = Binary_operation(lop=node, oper=token, rop=self.trm())

        return node

    def trm(self):
        node = self.fac()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = Binary_operation(lop=node, oper=token, rop=self.fac())

        return node

    def fac(self):
        token = self.current_token
        if token.type == ADD:
            self.eat(ADD)
            node = operator_uneray(token, self.fac())
            return node
        elif token.type == SUB:
            self.eat(SUB)
            node = operator_uneray(token, self.fac())
            return node
        elif token.type == INT:
            self.eat(INT)
            return int_value(token)
        elif token.type == LEFTBRAC:
            self.eat(LEFTBRAC)
            node = self.expr()
            self.eat(RIGHTBRAC)
            return node
        else:
            node = self.var()
            return node

    def parse(self):
        node = self.code()
        if self.current_token.type != EOF:
            self.invalid()

        return node


#interpreter
    
class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):

    GLOBAL_SCOPE = {}

    def __init__(self, parser):
        self.parser = parser

    def visit_Binary_operation(self, node):
        if node.op.type == ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == SUB:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_int_value(self, node):
        return node.value

    def visit_operator_uneray(self, node):
        op = node.op.type
        if op == ADD:
            return +self.visit(node.expr)
        elif op == SUB:
            return -self.visit(node.expr)

    def visit_begin_end(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assignment(self, node):
        var_name = node.left.value
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Value_var(self, node):
        var_name = node.value
        val = self.GLOBAL_SCOPE.get(var_name)
        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_No_Oper(self, node):
        pass

    def interpret(self):
        tree = self.parser.parse()
        if tree is None:
            return ''
        return self.visit(tree)


def main():
    import sys
    text = open("text2.txt", 'r').read()

    lexer = Lexer(text)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)
    result = interpreter.interpret()
    print(interpreter.GLOBAL_SCOPE)


if __name__ == '__main__':
    main()
