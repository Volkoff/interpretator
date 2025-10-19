"""
Parser for Oberon subset compiler
Builds AST from tokens
"""

from typing import List, Optional
from lexer import Lexer, Token, TokenType
from ast import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0] if tokens else None
    
    def parse(self) -> Program:
        """Parse the tokens into an AST"""
        return self.parse_program()
    
    def parse_program(self) -> Program:
        """Parse a complete program"""
        self.expect(TokenType.MODULE)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.SEMICOLON)
        
        declarations = []
        while self.current_token and self.current_token.type in [TokenType.CONST, TokenType.VAR, TokenType.PROCEDURE]:
            declarations.extend(self.parse_declaration())
        
        self.expect(TokenType.BEGIN)
        statements = []
        while self.current_token and self.current_token.type != TokenType.END:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.END)
        end_name = self.expect(TokenType.IDENTIFIER).value
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        self.expect(TokenType.DOT)
        
        if name != end_name:
            raise SyntaxError(f"Module name mismatch: {name} vs {end_name}")
        
        return Program(name, declarations, statements)
    
    def parse_declaration(self) -> List[Declaration]:
        """Parse a declaration"""
        if self.current_token.type == TokenType.CONST:
            return [self.parse_const_declaration()]
        elif self.current_token.type == TokenType.VAR:
            return self.parse_var_declaration()
        elif self.current_token.type == TokenType.PROCEDURE:
            return [self.parse_procedure_declaration()]
        else:
            raise SyntaxError(f"Unexpected token in declaration: {self.current_token}")
    
    def parse_const_declaration(self) -> ConstDeclaration:
        """Parse a constant declaration"""
        self.expect(TokenType.CONST)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.expect(TokenType.SEMICOLON)
        return ConstDeclaration(name, value)
    
    def parse_var_declaration(self) -> List[VarDeclaration]:
        """Parse variable declarations"""
        self.expect(TokenType.VAR)
        declarations = []
        
        while True:
            # Parse variable names
            names = [self.expect(TokenType.IDENTIFIER).value]
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                names.append(self.expect(TokenType.IDENTIFIER).value)
            
            self.expect(TokenType.COLON)
            
            if self.current_token.type == TokenType.ARRAY:
                self.advance()
                self.expect(TokenType.LBRACKET)
                size = int(self.expect(TokenType.INTEGER_LITERAL).value)
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.OF)
                type_token = self.expect(TokenType.INTEGER, TokenType.REAL, TokenType.STRING)
                type_ = DataType(type_token.value)
                
                for name in names:
                    declarations.append(VarDeclaration(name, type_, size))
            else:
                type_token = self.expect(TokenType.INTEGER, TokenType.REAL, TokenType.STRING)
                type_ = DataType(type_token.value)
                
                for name in names:
                    declarations.append(VarDeclaration(name, type_))
            
            self.expect(TokenType.SEMICOLON)
            
            # Check if there are more variable declarations
            if self.current_token.type != TokenType.IDENTIFIER:
                break
        
        return declarations
    
    def parse_procedure_declaration(self) -> ProcedureDeclaration:
        """Parse a procedure declaration"""
        self.expect(TokenType.PROCEDURE)
        name = self.expect(TokenType.IDENTIFIER).value
        
        parameters = []
        if self.current_token.type == TokenType.LPAREN:
            self.advance()
            if self.current_token.type != TokenType.RPAREN:
                parameters = self.parse_parameters()
            self.expect(TokenType.RPAREN)
        
        return_type = None
        if self.current_token.type == TokenType.COLON:
            self.advance()
            type_token = self.expect(TokenType.INTEGER, TokenType.REAL, TokenType.STRING)
            return_type = DataType(type_token.value)
        
        self.expect(TokenType.SEMICOLON)
        
        declarations = []
        while self.current_token and self.current_token.type in [TokenType.CONST, TokenType.VAR, TokenType.PROCEDURE]:
            declarations.append(self.parse_declaration())
        
        self.expect(TokenType.BEGIN)
        statements = []
        while self.current_token and self.current_token.type != TokenType.END:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.END)
        end_name = self.expect(TokenType.IDENTIFIER).value
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        if name != end_name:
            raise SyntaxError(f"Procedure name mismatch: {name} vs {end_name}")
        
        return ProcedureDeclaration(name, parameters, return_type, declarations, statements)
    
    def parse_parameters(self) -> List[Parameter]:
        """Parse procedure parameters"""
        parameters = []
        is_reference = False
        
        if self.current_token.type == TokenType.VAR:
            is_reference = True
            self.advance()
        
        names = [self.expect(TokenType.IDENTIFIER).value]
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            names.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.COLON)
        
        if self.current_token.type == TokenType.ARRAY:
            self.advance()
            self.expect(TokenType.LBRACKET)
            size = int(self.expect(TokenType.INTEGER_LITERAL).value)
            self.expect(TokenType.RBRACKET)
            self.expect(TokenType.OF)
            type_token = self.expect(TokenType.INTEGER, TokenType.REAL, TokenType.STRING)
            type_ = DataType(type_token.value)
            # For simplicity, we'll treat arrays as the base type
        else:
            type_token = self.expect(TokenType.INTEGER, TokenType.REAL, TokenType.STRING)
            type_ = DataType(type_token.value)
        
        for name in names:
            parameters.append(Parameter(name, type_, is_reference))
        
        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()
            parameters.extend(self.parse_parameters())
        
        return parameters
    
    def parse_statement(self) -> Statement:
        """Parse a statement"""
        if self.current_token.type == TokenType.IDENTIFIER:
            # Could be assignment or procedure call
            name = self.current_token.value
            self.advance()
            
            if self.current_token.type == TokenType.LBRACKET:
                # Array access
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                self.expect(TokenType.ASSIGN)
                expression = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                array_access = ArrayAccess(name, index)
                return Assignment(array_access, expression)
            elif self.current_token.type == TokenType.ASSIGN:
                self.advance()
                expression = self.parse_expression()
                self.expect(TokenType.SEMICOLON)
                return Assignment(name, expression)
            else:
                # Procedure call
                arguments = []
                if self.current_token.type == TokenType.LPAREN:
                    self.advance()
                    if self.current_token.type != TokenType.RPAREN:
                        arguments = self.parse_arguments()
                    self.expect(TokenType.RPAREN)
                self.expect(TokenType.SEMICOLON)
                return ProcedureCall(name, arguments)
        
        elif self.current_token.type == TokenType.IF:
            return self.parse_if_statement()
        elif self.current_token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.parse_for_statement()
        elif self.current_token.type == TokenType.BEGIN:
            return self.parse_compound_statement()
        else:
            raise SyntaxError(f"Unexpected token in statement: {self.current_token}")
    
    def parse_if_statement(self) -> IfStatement:
        """Parse an if statement"""
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.THEN)
        then_statement = self.parse_statement()
        
        else_statement = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            else_statement = self.parse_statement()
        
        self.expect(TokenType.END)
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        return IfStatement(condition, then_statement, else_statement)
    
    def parse_while_statement(self) -> WhileStatement:
        """Parse a while statement"""
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.DO)
        
        # Parse statements until we find END
        statements = []
        while self.current_token and self.current_token.type != TokenType.END:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.END)
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        # Create a compound statement if we have multiple statements
        if len(statements) == 1:
            statement = statements[0]
        else:
            statement = CompoundStatement(statements)
        
        return WhileStatement(condition, statement)
    
    def parse_for_statement(self) -> ForStatement:
        """Parse a for statement"""
        self.expect(TokenType.FOR)
        variable = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        start = self.parse_expression()
        self.expect(TokenType.TO)
        end = self.parse_expression()
        self.expect(TokenType.DO)
        
        # Parse statements until we find END
        statements = []
        while self.current_token and self.current_token.type != TokenType.END:
            statements.append(self.parse_statement())
        
        self.expect(TokenType.END)
        if self.current_token and self.current_token.type == TokenType.SEMICOLON:
            self.advance()
        
        # Create a compound statement if we have multiple statements
        if len(statements) == 1:
            statement = statements[0]
        else:
            statement = CompoundStatement(statements)
        
        return ForStatement(variable, start, end, statement)
    
    def parse_compound_statement(self) -> CompoundStatement:
        """Parse a compound statement"""
        self.expect(TokenType.BEGIN)
        statements = []
        while self.current_token and self.current_token.type != TokenType.END:
            statements.append(self.parse_statement())
        self.expect(TokenType.END)
        return CompoundStatement(statements)
    
    def parse_arguments(self) -> List[Expression]:
        """Parse function arguments"""
        arguments = [self.parse_expression()]
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            arguments.append(self.parse_expression())
        return arguments
    
    def parse_expression(self) -> Expression:
        """Parse an expression with proper precedence"""
        return self.parse_or_expression()
    
    def parse_or_expression(self) -> Expression:
        """Parse OR expressions"""
        left = self.parse_and_expression()
        
        while self.current_token.type == TokenType.OR:
            operator = self.current_token.value
            self.advance()
            right = self.parse_and_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_and_expression(self) -> Expression:
        """Parse AND expressions"""
        left = self.parse_equality_expression()
        
        while self.current_token.type == TokenType.AND:
            operator = self.current_token.value
            self.advance()
            right = self.parse_equality_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_equality_expression(self) -> Expression:
        """Parse equality expressions"""
        left = self.parse_relational_expression()
        
        while self.current_token.type in [TokenType.EQUAL, TokenType.NOT_EQUAL]:
            operator = self.current_token.value
            self.advance()
            right = self.parse_relational_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_relational_expression(self) -> Expression:
        """Parse relational expressions"""
        left = self.parse_additive_expression()
        
        while self.current_token.type in [TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL]:
            operator = self.current_token.value
            self.advance()
            right = self.parse_additive_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_additive_expression(self) -> Expression:
        """Parse additive expressions"""
        left = self.parse_multiplicative_expression()
        
        while self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.current_token.value
            self.advance()
            right = self.parse_multiplicative_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_multiplicative_expression(self) -> Expression:
        """Parse multiplicative expressions"""
        left = self.parse_unary_expression()
        
        while self.current_token.type in [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.DIV, TokenType.MOD]:
            operator = self.current_token.value
            self.advance()
            right = self.parse_unary_expression()
            left = BinaryExpression(left, operator, right)
        
        return left
    
    def parse_unary_expression(self) -> Expression:
        """Parse unary expressions"""
        if self.current_token.type in [TokenType.PLUS, TokenType.MINUS]:
            operator = self.current_token.value
            self.advance()
            operand = self.parse_primary_expression()
            return UnaryExpression(operator, operand)
        
        return self.parse_primary_expression()
    
    def parse_primary_expression(self) -> Expression:
        """Parse primary expressions"""
        if self.current_token.type == TokenType.INTEGER_LITERAL:
            value = int(self.current_token.value)
            self.advance()
            return Literal(value, DataType.INTEGER)
        
        elif self.current_token.type == TokenType.REAL_LITERAL:
            value = float(self.current_token.value)
            self.advance()
            return Literal(value, DataType.REAL)
        
        elif self.current_token.type == TokenType.STRING_LITERAL:
            value = self.current_token.value
            self.advance()
            return Literal(value, DataType.STRING)
        
        elif self.current_token.type == TokenType.IDENTIFIER:
            name = self.current_token.value
            self.advance()
            
            if self.current_token.type == TokenType.LBRACKET:
                # Array access
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                return ArrayAccess(name, index)
            elif self.current_token.type == TokenType.LPAREN:
                # Function call
                self.advance()
                arguments = []
                if self.current_token.type != TokenType.RPAREN:
                    arguments = self.parse_arguments()
                self.expect(TokenType.RPAREN)
                return FunctionCall(name, arguments)
            else:
                # Variable
                return Variable(name)
        
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            expression = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expression
        
        else:
            raise SyntaxError(f"Unexpected token in expression: {self.current_token}")
    
    def expect(self, *expected_types: TokenType) -> Token:
        """Expect a token of a specific type"""
        if not self.current_token:
            raise SyntaxError("Unexpected end of input")
        
        if self.current_token.type not in expected_types:
            expected_str = " or ".join([t.value for t in expected_types])
            raise SyntaxError(f"Expected {expected_str}, got {self.current_token.type.value}")
        
        token = self.current_token
        self.advance()
        return token
    
    def advance(self):
        """Advance to the next token"""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = None

if __name__ == "__main__":
    # Test the parser
    test_code = """
    MODULE Test;
    VAR x: INTEGER;
    BEGIN
        x := 42;
    END Test.
    """
    
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    
    try:
        ast = parser.parse()
        print("Parsing successful!")
        print(f"Module: {ast.name}")
        print(f"Declarations: {len(ast.declarations)}")
        print(f"Statements: {len(ast.statements)}")
    except Exception as e:
        print(f"Parsing error: {e}")
