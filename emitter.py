from typing import List, Dict, Tuple, Optional
from ast import *


class LLVMEmitter:
    def __init__(self):
        self.lines: List[str] = []
        self.globals: List[str] = []
        self.string_constants: Dict[str, str] = {}
        self.reg_counter = 0
        self.label_counter = 0
        self.current_locals: Dict[str, str] = {}
        self.current_local_types: Dict[str, str] = {}  # LLVM type for each local
        self.current_arrays: Dict[str, Tuple[str, int]] = {}

    def new_reg(self) -> str:
        self.reg_counter += 1
        return f"%t{self.reg_counter}"

    def new_label(self, prefix: str = "L") -> str:
        self.label_counter += 1
        return f"{prefix}{self.label_counter}"

    def emit(self, line: str = ""):
        self.lines.append(line)

    def add_global_string(self, s: str) -> str:
        if s in self.string_constants:
            return self.string_constants[s]
        name = f".str{len(self.string_constants) + 1}"
        # store as null-terminated bytes
        lit = s.encode('utf8') + b"\00"
        self.string_constants[s] = name
        self.globals.append(f"@{name} = private constant [{len(lit)} x i8] c\"{self._escape_bytes(lit)}\"")
        return name

    def _escape_bytes(self, b: bytes) -> str:
        # produce C-style escaped bytes for LLVM string literal
        out = ''
        for byte in b:
            if 32 <= byte <= 126 and byte not in (34, 92):
                out += chr(byte)
            else:
                out += f"\\{byte:02X}"
        return out

    def llvm_type(self, dtype: DataType) -> str:
        if dtype == DataType.INTEGER:
            return 'i32'
        if dtype == DataType.REAL:
            return 'double'
        if dtype == DataType.STRING:
            return 'i8*'
        if dtype == DataType.ARRAY:
            return 'i8*'  # arrays will be passed as pointers in simple model
        return 'i32'

    def emit_program(self, program: Program) -> str:
        # header: declare printf
        self.emit('; ModuleID = \"oberon_module\"')
        self.emit('declare i32 @printf(i8*, ...)')
        self.emit('')

        # process globals (string constants will be emitted later)
        # emit function declarations (procedures)
        for decl in program.declarations:
            if isinstance(decl, ProcedureDeclaration):
                self.emit_function(decl)

        # emit main
        self.emit('define i32 @main() {')
        self.emit('entry:')
        # allocate top-level variables
        for decl in program.declarations:
            if isinstance(decl, VarDeclaration):
                self.allocate_local(decl.name, decl)

        # emit main statements
        for stmt in program.statements:
            self.emit_statement(stmt)

        self.emit('  ret i32 0')
        self.emit('}')

        # emit global string constants
        self.emit('')
        for g in self.globals:
            self.emit(g)

        return '\n'.join(self.lines)

    def allocate_local(self, name: str, decl: VarDeclaration):
        ty = self.llvm_type(decl.type)
        if decl.array_size is not None:
            # allocate array as [N x i32] on stack and keep pointer
            # we will allocate as i32* by using alloca and treat as pointer
            ptr = f"%{name}"
            self.current_locals[name] = ptr
            self.current_local_types[name] = ty
            self.emit(f"  {ptr} = alloca {ty}, align 8")
            # remember size for index checks (not enforced)
            self.current_arrays[name] = (ptr, decl.array_size)
        else:
            ptr = f"%{name}"
            self.current_locals[name] = ptr
            self.current_local_types[name] = ty
            self.emit(f"  {ptr} = alloca {ty}")

    def emit_function(self, proc: ProcedureDeclaration):
        # construct signature
        ret = 'void' if proc.return_type is None else self.llvm_type(proc.return_type)
        params_sig = []
        for p in proc.parameters:
            params_sig.append(f"{self.llvm_type(p.type)} %{p.name}")
        sig = ', '.join(params_sig)
        self.emit(f'define {ret} @{proc.name}({sig}) '+'{')
        self.emit('entry:')
        # set up locals for parameters
        old_locals = self.current_locals.copy()
        self.current_locals = {}
        for p in proc.parameters:
            # create local slot and store incoming param
            local_ptr = f"%{p.name}.addr"
            self.emit(f"  {local_ptr} = alloca {self.llvm_type(p.type)}")
            self.emit(f"  store {self.llvm_type(p.type)} %{p.name}, {self.llvm_type(p.type)}* {local_ptr}")
            self.current_locals[p.name] = local_ptr

        # allocate locals declared inside procedure
        for decl in proc.declarations:
            if isinstance(decl, VarDeclaration):
                ptr = f"%{decl.name}"
                self.current_locals[decl.name] = ptr
                self.emit(f"  {ptr} = alloca {self.llvm_type(decl.type)}")

        # emit body
        for stmt in proc.statements:
            self.emit_statement(stmt)

        # return: if function, try to load 'result' var
        if proc.return_type is None:
            self.emit('  ret void')
        else:
            if 'result' in self.current_locals:
                rptr = self.current_locals['result']
                rreg = self.new_reg()
                self.emit(f"  {rreg} = load {self.llvm_type(proc.return_type)}, {self.llvm_type(proc.return_type)}* {rptr}")
                self.emit(f"  ret {self.llvm_type(proc.return_type)} {rreg}")
            else:
                # default 0
                self.emit(f"  ret {self.llvm_type(proc.return_type)} 0")

        self.emit('}')
        # restore locals
        self.current_locals = old_locals

    def emit_statement(self, stmt: Statement):
        if isinstance(stmt, Assignment):
            val_reg, val_type = self.emit_expression(stmt.expression)
            if isinstance(stmt.variable, str):
                if stmt.variable not in self.current_locals:
                    # allocate on-the-fly
                    ptr = f"%{stmt.variable}"
                    self.current_locals[stmt.variable] = ptr
                    self.emit(f"  {ptr} = alloca {val_type}")
                ptr = self.current_locals[stmt.variable]
                self.emit(f"  store {val_type} {val_reg}, {val_type}* {ptr}")
            elif isinstance(stmt.variable, ArrayAccess):
                # compute index
                arr = stmt.variable.name
                idx_reg, _ = self.emit_expression(stmt.variable.index)
                if arr not in self.current_locals:
                    raise NameError(f"Array '{arr}' not defined for store")
                arr_ptr = self.current_locals[arr]
                elem_ptr = self.new_reg()
                # GEP into array: treat as pointer arithmetic for i32*
                self.emit(f"  {elem_ptr} = getelementptr inbounds i32, i32* {arr_ptr}, i32 {idx_reg}")
                self.emit(f"  store {val_type} {val_reg}, {val_type}* {elem_ptr}")

        elif isinstance(stmt, ProcedureCall):
            if stmt.name == 'Write' or stmt.name == 'WriteLn':
                for arg in stmt.arguments:
                    a_reg, a_type = self.emit_expression(arg)
                    # choose format based on type
                    if a_type == 'i32':
                        fmt_str = '%d'
                    elif a_type == 'double':
                        fmt_str = '%f'
                    else:  # i8*
                        fmt_str = '%s'
                    fmt = self.add_global_string(fmt_str)
                    fmt_ptr = self.new_reg()
                    self.emit(f"  {fmt_ptr} = getelementptr inbounds [{len(fmt_str)+1} x i8], [{len(fmt_str)+1} x i8]* @{fmt}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {fmt_ptr}, {a_type} {a_reg})")
                if stmt.name == 'WriteLn':
                    nl = self.add_global_string('\n')
                    nl_ptr = self.new_reg()
                    self.emit(f"  {nl_ptr} = getelementptr inbounds [{len('\n\00')} x i8], [{len('\n\00')} x i8]* @{nl}, i32 0, i32 0")
                    self.emit(f"  call i32 (i8*, ...) @printf(i8* {nl_ptr})")
            else:
                # user procedure call (no return)
                arg_vals = []
                for arg in stmt.arguments:
                    a_reg, a_type = self.emit_expression(arg)
                    arg_vals.append((a_reg, a_type))
                args_text = ', '.join([f"{t} {r}" for (r, t) in arg_vals])
                self.emit(f"  call void @{stmt.name}({args_text})")

        elif isinstance(stmt, IfStatement):
            cond_reg, cond_type = self.emit_expression(stmt.condition)
            # compare cond_reg != 0
            cmp = self.new_reg()
            self.emit(f"  {cmp} = icmp ne i32 {cond_reg}, 0")
            then_label = self.new_label('then')
            else_label = self.new_label('else')
            end_label = self.new_label('endif')
            self.emit(f"  br i1 {cmp}, label %{then_label}, label %{else_label}")
            # then
            self.emit(f"{then_label}:")
            self.emit_statement(stmt.then_statement)
            self.emit(f"  br label %{end_label}")
            # else
            self.emit(f"{else_label}:")
            if stmt.else_statement:
                self.emit_statement(stmt.else_statement)
            self.emit(f"  br label %{end_label}")
            # end
            self.emit(f"{end_label}:")

        elif isinstance(stmt, WhileStatement):
            start = self.new_label('while_start')
            body = self.new_label('while_body')
            end = self.new_label('while_end')
            self.emit(f"  br label %{start}")
            self.emit(f"{start}:")
            cond_reg, _ = self.emit_expression(stmt.condition)
            cmp = self.new_reg()
            self.emit(f"  {cmp} = icmp ne i32 {cond_reg}, 0")
            self.emit(f"  br i1 {cmp}, label %{body}, label %{end}")
            self.emit(f"{body}:")
            self.emit_statement(stmt.statement)
            self.emit(f"  br label %{start}")
            self.emit(f"{end}:")

        elif isinstance(stmt, ForStatement):
            # set loop variable
            start_reg, _ = self.emit_expression(stmt.start)
            end_reg, _ = self.emit_expression(stmt.end)
            # allocate loop var if needed
            if stmt.variable not in self.current_locals:
                ptr = f"%{stmt.variable}"
                self.current_locals[stmt.variable] = ptr
                self.emit(f"  {ptr} = alloca i32")
            ptr = self.current_locals[stmt.variable]
            self.emit(f"  store i32 {start_reg}, i32* {ptr}")
            loop_start = self.new_label('for_start')
            loop_body = self.new_label('for_body')
            loop_end = self.new_label('for_end')
            self.emit(f"  br label %{loop_start}")
            self.emit(f"{loop_start}:")
            cur = self.new_reg()
            self.emit(f"  {cur} = load i32, i32* {ptr}")
            cond = self.new_reg()
            self.emit(f"  {cond} = icmp sle i32 {cur}, {end_reg}")
            self.emit(f"  br i1 {cond}, label %{loop_body}, label %{loop_end}")
            self.emit(f"{loop_body}:")
            self.emit_statement(stmt.statement)
            # increment
            inc = self.new_reg()
            self.emit(f"  {inc} = add i32 {cur}, 1")
            self.emit(f"  store i32 {inc}, i32* {ptr}")
            self.emit(f"  br label %{loop_start}")
            self.emit(f"{loop_end}:")

        elif isinstance(stmt, CompoundStatement):
            for s in stmt.statements:
                self.emit_statement(s)
        else:
            raise NotImplementedError(f"Statement emission not implemented for {type(stmt)}")

    def emit_expression(self, expr: Expression) -> Tuple[str, str]:
        # returns (value_repr, llvm_type)
        if isinstance(expr, Literal):
            if expr.type == DataType.INTEGER:
                return (str(int(expr.value)), 'i32')
            if expr.type == DataType.REAL:
                # LLVM double constants use 0.0 etc
                return (str(float(expr.value)), 'double')
            if expr.type == DataType.STRING:
                name = self.add_global_string(expr.value)
                ptr = self.new_reg()
                self.emit(f"  {ptr} = getelementptr inbounds [{len(expr.value)+1} x i8], [{len(expr.value)+1} x i8]* @{name}, i32 0, i32 0")
                return (ptr, 'i8*')

        elif isinstance(expr, Variable):
            if expr.name not in self.current_locals:
                raise NameError(f"Variable '{expr.name}' not allocated")
            ptr = self.current_locals[expr.name]
            ty = self.current_local_types[expr.name]
            res = self.new_reg()
            self.emit(f"  {res} = load {ty}, {ty}* {ptr}")
            return (res, ty)

        elif isinstance(expr, ArrayAccess):
            if expr.name not in self.current_locals:
                raise NameError(f"Array '{expr.name}' not allocated")
            arr_ptr = self.current_locals[expr.name]
            ty = self.current_local_types[expr.name]
            idx_reg, _ = self.emit_expression(expr.index)
            elem_ptr = self.new_reg()
            self.emit(f"  {elem_ptr} = getelementptr inbounds {ty}, {ty}* {arr_ptr}, i32 {idx_reg}")
            val = self.new_reg()
            self.emit(f"  {val} = load {ty}, {ty}* {elem_ptr}")
            return (val, ty)

        elif isinstance(expr, FunctionCall):
            arg_vals = []
            for arg in expr.arguments:
                a_reg, a_type = self.emit_expression(arg)
                arg_vals.append((a_reg, a_type))
            args_text = ', '.join([f"{t} {r}" for (r, t) in arg_vals])
            ret_type = 'i32'  # assume integer return for simplicity
            res = self.new_reg()
            self.emit(f"  {res} = call {ret_type} @{expr.name}({args_text})")
            return (res, ret_type)

        elif isinstance(expr, BinaryExpression):
            l_reg, l_type = self.emit_expression(expr.left)
            r_reg, r_type = self.emit_expression(expr.right)
            # assume integer arithmetic if both i32
            if l_type == 'i32' and r_type == 'i32':
                if expr.operator == '+':
                    out = self.new_reg()
                    self.emit(f"  {out} = add i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == '-':
                    out = self.new_reg()
                    self.emit(f"  {out} = sub i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == '*':
                    out = self.new_reg()
                    self.emit(f"  {out} = mul i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == '/':
                    out = self.new_reg()
                    self.emit(f"  {out} = sdiv i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == 'DIV':
                    out = self.new_reg()
                    self.emit(f"  {out} = sdiv i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == 'MOD':
                    out = self.new_reg()
                    self.emit(f"  {out} = srem i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator in ('=', '#', '<', '<=', '>', '>='):
                    cmp = self.new_reg()
                    op_map = {'=': 'eq', '#': 'ne', '<': 'slt', '<=': 'sle', '>': 'sgt', '>=': 'sge'}
                    self.emit(f"  {cmp} = icmp {op_map[expr.operator]} i32 {l_reg}, {r_reg}")
                    z = self.new_reg()
                    self.emit(f"  {z} = zext i1 {cmp} to i32")
                    return (z, 'i32')
                if expr.operator == 'AND':
                    out = self.new_reg()
                    self.emit(f"  {out} = and i32 {l_reg}, {r_reg}")
                    return (out, 'i32')
                if expr.operator == 'OR':
                    out = self.new_reg()
                    self.emit(f"  {out} = or i32 {l_reg}, {r_reg}")
                    return (out, 'i32')

            # Fallback: treat as i32
            out = self.new_reg()
            self.emit(f"  {out} = add i32 {l_reg}, {r_reg}")
            return (out, 'i32')

        elif isinstance(expr, UnaryExpression):
            op_reg, op_type = self.emit_expression(expr.operand)
            if expr.operator == '-':
                out = self.new_reg()
                self.emit(f"  {out} = sub i32 0, {op_reg}")
                return (out, 'i32')
            return (op_reg, op_type)

        else:
            raise NotImplementedError(f"Expression emission not implemented for {type(expr)}")
