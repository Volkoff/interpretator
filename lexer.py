import re
from enum import Enum
from typing import List, Optional, Tuple

class TokenType(Enum):
    MODULE = "MODULE"
    BEGIN = "BEGIN"
    END = "END"
    CONST = "CONST"
    VAR = "VAR"
    PROCEDURE = "PROCEDURE"
    IF = "IF"
    THEN = "THEN"
    ELSE = "ELSE"
    WHILE = "WHILE"
    DO = "DO"
    FOR = "FOR"
    TO = "TO"
    RETURN = "RETURN"
    
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    ARRAY = "ARRAY"
    OF = "OF"
    
    ASSIGN = ":="
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    DIV = "DIV"
    MOD = "MOD"
    AND = "AND"
    OR = "OR"
    
    EQUAL = "="
    NOT_EQUAL = "#"
    LESS = "<"
    LESS_EQUAL = "<="
    GREATER = ">"
    GREATER_EQUAL = ">="
    
    SEMICOLON = ";"
    COLON = ":"
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACKET = "["
    RBRACKET = "]"
    DOT = "."
    
    IDENTIFIER = "IDENTIFIER"
    INTEGER_LITERAL = "INTEGER_LITERAL"
    REAL_LITERAL = "REAL_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    
    EOF = "EOF"
    NEWLINE = "NEWLINE"

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type.value}, '{self.value}', {self.line}:{self.column})"

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        self.keywords = {
            'MODULE': TokenType.MODULE,
            'BEGIN': TokenType.BEGIN,
            'END': TokenType.END,
            'CONST': TokenType.CONST,
            'VAR': TokenType.VAR,
            'PROCEDURE': TokenType.PROCEDURE,
            'IF': TokenType.IF,
            'THEN': TokenType.THEN,
            'ELSE': TokenType.ELSE,
            'WHILE': TokenType.WHILE,
            'DO': TokenType.DO,
            'FOR': TokenType.FOR,
            'TO': TokenType.TO,
            'RETURN': TokenType.RETURN,
            'INTEGER': TokenType.INTEGER,
            'REAL': TokenType.REAL,
            'STRING': TokenType.STRING,
            'ARRAY': TokenType.ARRAY,
            'OF': TokenType.OF,
            'DIV': TokenType.DIV,
            'MOD': TokenType.MOD,
            'AND': TokenType.AND,
            'OR': TokenType.OR
        }
    
    def tokenize(self) -> List[Token]:
        """Tokenizuje zdrojovy kod"""
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if self.position >= len(self.source):
                break
                
            char = self.source[self.position]
            
            if char.isalpha() or char == '_':
                self.read_identifier()
            elif char.isdigit():
                self.read_number()
            elif char == '"':
                self.read_string()
            elif char == ':':
                if self.peek() == '=':
                    self.add_token(TokenType.ASSIGN, ":=")
                    self.advance()
                else:
                    self.add_token(TokenType.COLON, ":")
            elif char == '<':
                if self.peek() == '=':
                    self.add_token(TokenType.LESS_EQUAL, "<=")
                    self.advance()
                else:
                    self.add_token(TokenType.LESS, "<")
            elif char == '>':
                if self.peek() == '=':
                    self.add_token(TokenType.GREATER_EQUAL, ">=")
                    self.advance()
                else:
                    self.add_token(TokenType.GREATER, ">")
            elif char == '#':
                self.add_token(TokenType.NOT_EQUAL, "#")
            elif char == '+':
                self.add_token(TokenType.PLUS, "+")
            elif char == '-':
                self.add_token(TokenType.MINUS, "-")
            elif char == '*':
                self.add_token(TokenType.MULTIPLY, "*")
            elif char == '/':
                self.add_token(TokenType.DIVIDE, "/")
            elif char == '=':
                self.add_token(TokenType.EQUAL, "=")
            elif char == ';':
                self.add_token(TokenType.SEMICOLON, ";")
            elif char == ',':
                self.add_token(TokenType.COMMA, ",")
            elif char == '(':
                self.add_token(TokenType.LPAREN, "(")
            elif char == ')':
                self.add_token(TokenType.RPAREN, ")")
            elif char == '[':
                self.add_token(TokenType.LBRACKET, "[")
            elif char == ']':
                self.add_token(TokenType.RBRACKET, "]")
            elif char == '.':
                self.add_token(TokenType.DOT, ".")
            else:
                raise SyntaxError(f"Unexpected character '{char}' at line {self.line}, column {self.column}")
            
            self.advance()
        
        self.add_token(TokenType.EOF, "")
        return self.tokens
    
    def read_identifier(self):
        """Cte identifikator nebo klicove slovo"""
        start = self.position
        while self.position < len(self.source) and (self.source[self.position].isalnum() or self.source[self.position] == '_'):
            self.advance()
        
        value = self.source[start:self.position]
        token_type = self.keywords.get(value.upper(), TokenType.IDENTIFIER)
        self.add_token(token_type, value)
        self.position -= 1
    
    def read_number(self):
        """Cte cislo (cele nebo realne)"""
        start = self.position
        while self.position < len(self.source) and self.source[self.position].isdigit():
            self.advance()
        
        if self.position < len(self.source) and self.source[self.position] == '.':
            self.advance()
            while self.position < len(self.source) and self.source[self.position].isdigit():
                self.advance()
            value = self.source[start:self.position]
            self.add_token(TokenType.REAL_LITERAL, value)
        else:
            value = self.source[start:self.position]
            self.add_token(TokenType.INTEGER_LITERAL, value)
        
        self.position -= 1
    
    def read_string(self):
        """Cte retezec"""
        self.advance()
        start = self.position
        
        while self.position < len(self.source) and self.source[self.position] != '"':
            self.advance()
        
        if self.position >= len(self.source):
            raise SyntaxError(f"Unterminated string at line {self.line}, column {self.column}")
        
        value = self.source[start:self.position]
        self.add_token(TokenType.STRING_LITERAL, value)
    
    def skip_whitespace(self):
        """Preskakuje mezery a komentare"""
        while self.position < len(self.source):
            if self.source[self.position].isspace():
                if self.source[self.position] == '\n':
                    self.line += 1
                    self.column = 1
                self.advance()
            elif self.position + 1 < len(self.source) and self.source[self.position] == '(' and self.source[self.position + 1] == '*':
                self.advance()
                self.advance()
                while self.position < len(self.source):
                    if self.position + 1 < len(self.source) and self.source[self.position] == '*' and self.source[self.position + 1] == ')':
                        self.advance()
                        self.advance()
                        break
                    if self.source[self.position] == '\n':
                        self.line += 1
                        self.column = 1
                    self.advance()
            else:
                break
    
    def peek(self, offset: int = 1) -> Optional[str]:
        """Vrací další znak bez posunu"""
        if self.position + offset < len(self.source):
            return self.source[self.position + offset]
        return None
    
    def advance(self):
        """Posune se na dalsi znak"""
        if self.position < len(self.source):
            self.position += 1
            self.column += 1
    
    def add_token(self, token_type: TokenType, value: str):
        """Prida token do seznamu"""
        token = Token(token_type, value, self.line, self.column)
        self.tokens.append(token)