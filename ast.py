"""
Abstract Syntax Tree nodes for Oberon subset compiler
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
from enum import Enum

class DataType(Enum):
    INTEGER = "INTEGER"
    REAL = "REAL"
    STRING = "STRING"
    ARRAY = "ARRAY"

class ASTNode(ABC):
    """Base class for all AST nodes"""
    pass

class Program(ASTNode):
    def __init__(self, name: str, declarations: List['Declaration'], statements: List['Statement']):
        self.name = name
        self.declarations = declarations
        self.statements = statements

class Declaration(ASTNode):
    pass

class ConstDeclaration(Declaration):
    def __init__(self, name: str, value: 'Expression'):
        self.name = name
        self.value = value

class VarDeclaration(Declaration):
    def __init__(self, name: str, type_: DataType, array_dimensions: Optional[List[int]] = None):
        self.name = name
        self.type = type_
        # array_dimensions je List[int] pro vícerozměrná pole (např. [10, 20] pro ARRAY 10, 20 OF INTEGER)
        # nebo None pro jednoduchou proměnnou
        self.array_dimensions = array_dimensions
        # Backwards compatibility: pokud byl volán se starým array_size
        self.array_size = array_dimensions[0] if array_dimensions and len(array_dimensions) == 1 else None

class ProcedureDeclaration(Declaration):
    def __init__(self, name: str, parameters: List['Parameter'], return_type: Optional[DataType], 
                 declarations: List[Declaration], statements: List['Statement']):
        self.name = name
        self.parameters = parameters
        self.return_type = return_type
        self.declarations = declarations
        self.statements = statements

class Parameter(ASTNode):
    def __init__(self, name: str, type_: DataType, is_reference: bool = False):
        self.name = name
        self.type = type_
        self.is_reference = is_reference

class Statement(ASTNode):
    pass

class Assignment(Statement):
    def __init__(self, variable: Union[str, 'ArrayAccess'], expression: 'Expression'):
        self.variable = variable
        self.expression = expression

class ProcedureCall(Statement):
    def __init__(self, name: str, arguments: List['Expression']):
        self.name = name
        self.arguments = arguments

class IfStatement(Statement):
    def __init__(self, condition: 'Expression', then_statement: Statement, else_statement: Optional[Statement] = None):
        self.condition = condition
        self.then_statement = then_statement
        self.else_statement = else_statement

class WhileStatement(Statement):
    def __init__(self, condition: 'Expression', statement: Statement):
        self.condition = condition
        self.statement = statement

class ForStatement(Statement):
    def __init__(self, variable: str, start: 'Expression', end: 'Expression', statement: Statement):
        self.variable = variable
        self.start = start
        self.end = end
        self.statement = statement

class CompoundStatement(Statement):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

class Expression(ASTNode):
    pass

class BinaryExpression(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

class UnaryExpression(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

class Literal(Expression):
    def __init__(self, value: Union[int, float, str], type_: DataType):
        self.value = value
        self.type = type_

class Variable(Expression):
    def __init__(self, name: str, array_index: Optional[Expression] = None):
        self.name = name
        self.array_index = array_index

class FunctionCall(Expression):
    def __init__(self, name: str, arguments: List[Expression]):
        self.name = name
        self.arguments = arguments

class ArrayAccess(Expression):
    def __init__(self, name: str, indices: List[Expression]):
        self.name = name
        # indices je List[Expression] pro vícerozměrná pole (např. [i, j] pro a[i, j])
        self.indices = indices
        # Backwards compatibility
        self.index = indices[0] if indices and len(indices) == 1 else None
