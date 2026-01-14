"""
C Code Emitter for Oberon Compiler
Converts AST to C code that can be compiled with GCC
"""

from oberon_ast import *
from enum import Enum


class CEmitter:
    """Emits C code from Oberon AST"""
    
    def __init__(self):
        self.code = []
        self.indent_level = 0
        self.variables = {}  # Track variable types: name -> DataType
    
    def emit(self, text=""):
        """Emit a line of code with proper indentation"""
        if text:
            self.code.append("    " * self.indent_level + text)
        else:
            self.code.append("")
    
    def emit_program(self, ast):
        """Generate complete C program from Oberon AST"""
        self.code = []
        
        # Include standard headers
        self.emit("#include <stdio.h>")
        self.emit("#include <stdlib.h>")
        self.emit("#include <string.h>")
        self.emit()
        
        # First pass: emit forward declarations for procedures
        if hasattr(ast, 'declarations') and ast.declarations:
            for decl in ast.declarations:
                if isinstance(decl, ProcedureDeclaration):
                    self._emit_procedure_forward_decl(decl)
            if any(isinstance(d, ProcedureDeclaration) for d in ast.declarations):
                self.emit()
        
        # Emit variable declarations (global scope)
        if hasattr(ast, 'declarations') and ast.declarations:
            for decl in ast.declarations:
                if isinstance(decl, VarDeclaration):
                    self._emit_var_decl(decl, is_global=True)
        
        self.emit()
        
        # Second pass: emit procedure implementations
        if hasattr(ast, 'declarations') and ast.declarations:
            for decl in ast.declarations:
                if isinstance(decl, ProcedureDeclaration):
                    self._emit_procedure_decl(decl)
        
        # Emit main function
        self.emit("int main() {")
        self.indent_level += 1
        
        # Emit statements from the main block
        if hasattr(ast, 'statements') and ast.statements:
            for stmt in ast.statements:
                self._emit_statement(stmt)
        
        self.emit("return 0;")
        self.indent_level -= 1
        self.emit("}")
        
        return "\n".join(self.code)
    
    def _emit_procedure_forward_decl(self, proc):
        """Emit procedure forward declaration (prototype)"""
        return_type = "void"
        if hasattr(proc, 'return_type') and proc.return_type:
            return_type = self._get_c_type(proc.return_type)
        
        params = ""
        if hasattr(proc, 'parameters') and proc.parameters:
            param_list = []
            for param in proc.parameters:
                param_type = self._get_c_type(param.type) if hasattr(param, 'type') else "int"
                # Handle array parameters
                if hasattr(param, 'array_dimensions') and param.array_dimensions:
                    # Array parameter: use pointer syntax
                    param_list.append(f"{param_type} *{param.name}")
                else:
                    param_list.append(f"{param_type} {param.name}")
            params = ", ".join(param_list)
        
        self.emit(f"{return_type} {proc.name}({params});")
    
    def _emit_var_decl(self, decl, is_global=False):
        """Emit variable declaration"""
        if not decl.type:
            c_type = "int"  # Default type
            dtype = DataType.INTEGER
        else:
            c_type = self._get_c_type(decl.type)
            dtype = decl.type if isinstance(decl.type, DataType) else None
        
        # Track variable type
        self.variables[decl.name] = dtype
        
        # Handle arrays - check both 'dimensions' and 'array_dimensions' attributes
        dims = getattr(decl, 'array_dimensions', None) or getattr(decl, 'dimensions', None)
        if dims:
            # For arrays, track that this is an array and store dimension info
            self.variables[decl.name] = (dtype, dims)  # Store dimensions
            dim_str = "".join(f"[{d}]" for d in dims)
            # Use base type (int) for arrays, not char*
            base_type = self._get_c_type(dtype) if isinstance(dtype, DataType) else "int"
            self.emit(f"{base_type} {decl.name}{dim_str};")
        else:
            self.emit(f"{c_type} {decl.name};")
    
    def _emit_procedure_decl(self, proc):
        """Emit procedure declaration"""
        # Determine return type
        return_type = "void"
        if hasattr(proc, 'return_type') and proc.return_type:
            return_type = self._get_c_type(proc.return_type)
        
        # Procedure signature
        params = ""
        if hasattr(proc, 'parameters') and proc.parameters:
            param_list = []
            for param in proc.parameters:
                param_type = self._get_c_type(param.type) if hasattr(param, 'type') else "int"
                # Handle array parameters
                if hasattr(param, 'array_dimensions') and param.array_dimensions:
                    # Array parameter: use pointer syntax
                    param_list.append(f"{param_type} *{param.name}")
                else:
                    param_list.append(f"{param_type} {param.name}")
            params = ", ".join(param_list)
        
        self.emit(f"{return_type} {proc.name}({params}) {{")
        self.indent_level += 1
        
        # Emit local variables
        if hasattr(proc, 'declarations') and proc.declarations:
            # First pass: emit nested procedure forward declarations
            for decl in proc.declarations:
                if isinstance(decl, ProcedureDeclaration):
                    self._emit_procedure_forward_decl(decl)
            
            # Second pass: emit variable declarations
            for decl in proc.declarations:
                if isinstance(decl, VarDeclaration):
                    self._emit_var_decl(decl)
            
            # Third pass: emit nested procedures
            for decl in proc.declarations:
                if isinstance(decl, ProcedureDeclaration):
                    self._emit_procedure_decl(decl)
        
        # Emit procedure body
        if hasattr(proc, 'statements') and proc.statements:
            for stmt in proc.statements:
                self._emit_statement(stmt)
        
        self.indent_level -= 1
        self.emit("}")
        self.emit()
    
    def _emit_statement(self, stmt):
        """Emit a statement"""
        if stmt is None:
            return
        
        if isinstance(stmt, Assignment):
            self._emit_assignment(stmt)
        elif isinstance(stmt, ProcedureCall):
            self._emit_procedure_call(stmt)
        elif isinstance(stmt, IfStatement):
            self._emit_if_statement(stmt)
        elif isinstance(stmt, WhileStatement):
            self._emit_while_statement(stmt)
        elif isinstance(stmt, ForStatement):
            self._emit_for_statement(stmt)
        elif isinstance(stmt, CompoundStatement):
            if hasattr(stmt, 'statements') and stmt.statements:
                for s in stmt.statements:
                    self._emit_statement(s)
        elif isinstance(stmt, ReturnStatement):
            # ReturnStatement uses 'expression' attribute
            if hasattr(stmt, 'expression') and stmt.expression:
                expr = self._emit_expression(stmt.expression)
                self.emit(f"return {expr};")
            else:
                self.emit("return;")
    
    def _emit_assignment(self, stmt):
        """Emit assignment statement"""
        # Handle variable assignment or array access assignment
        if isinstance(stmt.variable, ArrayAccess):
            # Array assignment: arr[0] := value
            name = stmt.variable.name
            # Get all indices
            indices = []
            for idx in stmt.variable.indices:
                indices.append(self._emit_expression(idx))
            # Build array access: arr[0][1] etc for multi-dimensional
            target = name
            for idx in indices:
                target = f"{target}[{idx}]"
        elif isinstance(stmt.variable, Variable):
            # Simple variable assignment
            if stmt.variable.array_index:
                idx = self._emit_expression(stmt.variable.array_index)
                target = f"{stmt.variable.name}[{idx}]"
            else:
                target = stmt.variable.name
        elif isinstance(stmt.variable, str):
            target = stmt.variable
        else:
            target = self._emit_lvalue(stmt.variable)
        
        value = self._emit_expression(stmt.expression)
        self.emit(f"{target} = {value};")
    
    def _emit_lvalue(self, lvalue):
        """Emit left-hand side of assignment (variable or array access)"""
        if isinstance(lvalue, Variable):
            if lvalue.array_index:
                idx = self._emit_expression(lvalue.array_index)
                return f"{lvalue.name}[{idx}]"
            return lvalue.name
        elif isinstance(lvalue, str):
            return lvalue
        else:
            return str(lvalue)
    
    def _emit_procedure_call(self, call):
        """Emit procedure call statement"""
        if call.name == "WriteLn":
            self._emit_writeln(call)
        elif call.name == "Write":
            self._emit_write(call)
        elif call.name == "ReadLn":
            self._emit_readln(call)
        elif call.name == "Read":
            self._emit_read(call)
        else:
            # Regular procedure call
            args = ""
            if hasattr(call, 'arguments') and call.arguments:
                args = ", ".join(self._emit_expression(arg) for arg in call.arguments)
            self.emit(f"{call.name}({args});")
    
    def _emit_write(self, call):
        """Emit Write (no newline) call"""
        if hasattr(call, 'arguments') and call.arguments:
            for arg in call.arguments:
                fmt = self._get_format_specifier(arg)
                expr = self._emit_expression(arg)
                self.emit(f'printf("{fmt}", {expr});')
    
    def _emit_writeln(self, call):
        """Emit WriteLn (with newline) call"""
        if hasattr(call, 'arguments') and call.arguments:
            # Combine all arguments into one format string
            format_parts = []
            args = []
            for arg in call.arguments:
                fmt = self._get_format_specifier(arg)
                expr = self._emit_expression(arg)
                format_parts.append(fmt)
                args.append(expr)
            
            format_str = "".join(format_parts) + "\\n"
            args_str = ", ".join(args)
            self.emit(f'printf("{format_str}", {args_str});')
        else:
            self.emit('printf("\\n");')
    
    def _emit_read(self, call):
        """Emit Read call"""
        if hasattr(call, 'arguments') and call.arguments:
            for arg in call.arguments:
                var = self._emit_lvalue(arg)
                self.emit(f'scanf("%d", &{var});')
    
    def _emit_readln(self, call):
        """Emit ReadLn call"""
        if hasattr(call, 'arguments') and call.arguments:
            for arg in call.arguments:
                var = self._emit_lvalue(arg)
                self.emit(f'scanf("%d", &{var});')
    
    def _get_format_specifier(self, expr):
        """Determine printf format specifier for expression"""
        if isinstance(expr, Literal):
            if expr.type == DataType.INTEGER:
                return "%d"
            elif expr.type == DataType.REAL:
                return "%f"
            elif expr.type == DataType.STRING:
                return "%s"
            else:
                return "%s"  # Default to string
        elif isinstance(expr, ArrayAccess):
            # For array access, check the array's type
            var_type = self.variables.get(expr.name)
            if isinstance(var_type, tuple):
                var_type = var_type[0]
            if var_type == DataType.REAL:
                return "%f"
            elif var_type == DataType.STRING:
                return "%s"
            else:
                return "%d"  # Default to int for arrays
        elif isinstance(expr, Variable):
            # Check if we know the variable type
            var_type = self.variables.get(expr.name)
            # Handle tuples (type, dimensions) for arrays
            if isinstance(var_type, tuple):
                var_type = var_type[0]
            if var_type == DataType.STRING:
                return "%s"
            elif var_type == DataType.REAL:
                return "%f"
            elif var_type == DataType.INTEGER:
                return "%d"
            else:
                return "%d"  # Default to int
        else:
            return "%s"
    
    def _emit_if_statement(self, stmt):
        """Emit if statement"""
        condition = self._emit_expression(stmt.condition)
        self.emit(f"if ({condition}) {{")
        self.indent_level += 1
        
        # Emit then statement (singular, might be CompoundStatement)
        if hasattr(stmt, 'then_statement') and stmt.then_statement:
            self._emit_statement(stmt.then_statement)
        
        self.indent_level -= 1
        
        if hasattr(stmt, 'else_statement') and stmt.else_statement:
            self.emit("} else {")
            self.indent_level += 1
            self._emit_statement(stmt.else_statement)
            self.indent_level -= 1
        
        self.emit("}")
    
    def _emit_while_statement(self, stmt):
        """Emit while statement"""
        condition = self._emit_expression(stmt.condition)
        self.emit(f"while ({condition}) {{")
        self.indent_level += 1
        
        # Emit statement body (singular, might be CompoundStatement)
        if hasattr(stmt, 'statement') and stmt.statement:
            self._emit_statement(stmt.statement)
        
        self.indent_level -= 1
        self.emit("}")
    
    def _emit_for_statement(self, stmt):
        """Emit for statement"""
        # Oberon FOR: FOR var := start TO end DO ... END
        var = stmt.variable
        start = self._emit_expression(stmt.start)
        end = self._emit_expression(stmt.end)
        step = "1"
        if hasattr(stmt, 'step') and stmt.step:
            step = self._emit_expression(stmt.step)
        
        self.emit(f"for ({var} = {start}; {var} <= {end}; {var} += {step}) {{")
        self.indent_level += 1
        
        # The body is a single statement (might be CompoundStatement for multiple statements)
        if hasattr(stmt, 'statement') and stmt.statement:
            self._emit_statement(stmt.statement)
        
        self.indent_level -= 1
        self.emit("}")
    
    def _emit_expression(self, expr):
        """Emit expression and return as string"""
        if expr is None:
            return "0"
        elif isinstance(expr, Literal):
            if expr.type == DataType.STRING:
                # Escape string value
                escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            else:
                return str(expr.value)
        elif isinstance(expr, Variable):
            if expr.array_index:
                idx = self._emit_expression(expr.array_index)
                return f"{expr.name}[{idx}]"
            return expr.name
        elif isinstance(expr, ArrayAccess):
            # Handle multi-dimensional arrays
            name = expr.name
            for idx in expr.indices:
                idx_expr = self._emit_expression(idx)
                name = f"{name}[{idx_expr}]"
            return name
        elif isinstance(expr, BinaryExpression):
            left = self._emit_expression(expr.left)
            right = self._emit_expression(expr.right)
            op = self._map_binary_operator(expr.operator)
            return f"({left} {op} {right})"
        elif isinstance(expr, UnaryExpression):
            operand = self._emit_expression(expr.operand)
            op = self._map_unary_operator(expr.operator)
            return f"{op}({operand})"
        elif isinstance(expr, FunctionCall):
            args = ""
            if hasattr(expr, 'arguments') and expr.arguments:
                args = ", ".join(self._emit_expression(arg) for arg in expr.arguments)
            return f"{expr.name}({args})"
        else:
            return str(expr)
    
    def _map_binary_operator(self, op):
        """Map Oberon binary operator to C operator"""
        op_map = {
            '+': '+',
            '-': '-',
            '*': '*',
            '/': '/',
            'DIV': '/',
            'MOD': '%',
            'AND': '&&',
            'OR': '||',
            '=': '==',
            '<>': '!=',
            '!=': '!=',
            '<': '<',
            '>': '>',
            '<=': '<=',
            '>=': '>=',
        }
        return op_map.get(op, op)
    
    def _map_unary_operator(self, op):
        """Map Oberon unary operator to C operator"""
        op_map = {
            '-': '-',
            '+': '+',
            'NOT': '!',
        }
        return op_map.get(op, op)
    
    def _get_c_type(self, dtype):
        """Map Oberon DataType to C type"""
        if isinstance(dtype, str):
            # Handle string type names
            type_map = {
                'INTEGER': 'int',
                'REAL': 'double',
                'STRING': 'char*',
                'ARRAY': 'int*',
            }
            return type_map.get(dtype.upper(), 'int')
        elif isinstance(dtype, DataType):
            # Handle DataType enum
            if dtype == DataType.INTEGER:
                return 'int'
            elif dtype == DataType.REAL:
                return 'double'
            elif dtype == DataType.STRING:
                return 'char*'
            elif dtype == DataType.ARRAY:
                return 'int*'
        return 'int'  # Default type



