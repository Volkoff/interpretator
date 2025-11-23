"""
GUI Application for Oberon Compiler
A modern interface for writing, compiling, and running Oberon programs
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, font
import sys
import os
from typing import List, Optional
import threading
import time

# Import compiler components
from lexer import Lexer, TokenType
from parser import Parser
from semantic_analyzer import SemanticAnalyzer
from interpreter import Interpreter
from compiler import Compiler

class OberonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Oberon Compiler IDE")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Compiler instance
        self.compiler = Compiler()
        self.current_file = None
        self.is_compiling = False
        
        # Configure styles
        self.setup_styles()
        
        # Create GUI components
        self.create_widgets()
        self.setup_menus()
        self.setup_bindings()
        
        # Load example code
        self.load_example_code()
    
    def setup_styles(self):
        """Configure custom styles for the GUI"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.colors = {
            'bg': '#f8f9fa',
            'editor_bg': '#ffffff',
            'output_bg': '#1e1e1e',
            'output_fg': '#d4d4d4',
            'error_fg': '#f44747',
            'success_fg': '#4ec9b0',
            'keyword_fg': '#569cd6',
            'string_fg': '#ce9178',
            'comment_fg': '#6a9955',
            'number_fg': '#b5cea8'
        }
    
    def create_widgets(self):
        """Create the main GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Left panel - Code editor
        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Editor frame with label
        editor_label_frame = ttk.LabelFrame(left_frame, text="Oberon Code Editor", padding=5)
        editor_label_frame.pack(fill=tk.BOTH, expand=True)
        
        # Code editor with syntax highlighting
        self.editor = scrolledtext.ScrolledText(
            editor_label_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg=self.colors['editor_bg'],
            fg='#000000',
            insertbackground='#000000',
            selectbackground='#3399ff',
            selectforeground='#ffffff',
            undo=True,
            maxundo=50
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Right panel - Output and controls
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # Output frame
        output_label_frame = ttk.LabelFrame(right_frame, text="Output", padding=5)
        output_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Output text widget
        self.output_text = scrolledtext.ScrolledText(
            output_label_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg=self.colors['output_bg'],
            fg=self.colors['output_fg'],
            insertbackground=self.colors['output_fg'],
            state=tk.DISABLED,
            height=15
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # Status frame
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready", font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=(10, 0))
    
    def create_toolbar(self, parent):
        """Create the toolbar with buttons"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # File operations
        ttk.Button(toolbar, text="New", command=self.new_file, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Open", command=self.open_file, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save", command=self.save_file, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Save As", command=self.save_as_file, width=8).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Compilation
        ttk.Button(toolbar, text="Compile", command=self.compile_code, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Run", command=self.run_code, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar, text="Clear", command=self.clear_output, width=8).pack(side=tk.LEFT, padx=(0, 5))
        
        # Separator
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Examples
        ttk.Button(toolbar, text="Examples", command=self.show_examples, width=10).pack(side=tk.LEFT, padx=(0, 5))
    
    def setup_menus(self):
        """Setup the menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.editor.edit_undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.editor.edit_redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self.select_all_text, accelerator="Ctrl+A")
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Run", menu=run_menu)
        run_menu.add_command(label="Compile", command=self.compile_code, accelerator="F5")
        run_menu.add_command(label="Run", command=self.run_code, accelerator="F6")
        run_menu.add_command(label="Compile & Run", command=self.compile_and_run, accelerator="F7")
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Oberon Syntax", command=self.show_syntax_help)
    
    def setup_bindings(self):
        """Setup keyboard shortcuts and other bindings"""
        # Keyboard shortcuts
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_as_file())
        self.root.bind('<F5>', lambda e: self.compile_code())
        self.root.bind('<F6>', lambda e: self.run_code())
        self.root.bind('<F7>', lambda e: self.compile_and_run())
        
        # Copy/paste shortcuts
        self.root.bind('<Control-x>', lambda e: self.cut_text())
        self.root.bind('<Control-c>', lambda e: self.copy_text())
        self.root.bind('<Control-v>', lambda e: self.paste_text())
        self.root.bind('<Control-a>', lambda e: self.select_all_text())
        
        # Editor bindings for syntax highlighting and tab handling
        self.editor.bind('<KeyRelease>', self.on_editor_change)
        self.editor.bind('<Button-1>', self.on_editor_click)
        self.editor.bind('<Tab>', self.on_tab_press)
        
        # Configure tab width
        self.editor.configure(tabs=4)
    
    def load_example_code(self):
        """Load example Oberon code into the editor"""
        example_code = """MODULE HelloWorld;
VAR message: STRING;
BEGIN
    message := "Hello, World!";
    Write(message);
    WriteLn();
END HelloWorld."""
        
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, example_code)
        self.apply_syntax_highlighting()
    
    def on_editor_change(self, event=None):
        """Handle editor content changes"""
        if not self.is_compiling:
            self.apply_syntax_highlighting()
    
    def on_editor_click(self, event=None):
        """Handle editor clicks"""
        pass
    
    def apply_syntax_highlighting(self):
        """Apply syntax highlighting to the editor"""
        # Clear existing tags
        for tag in self.editor.tag_names():
            if tag not in ['sel', 'insert']:
                self.editor.tag_delete(tag)
        
        # Get the content
        content = self.editor.get(1.0, tk.END)
        
        # Define syntax highlighting patterns
        keywords = [
            'MODULE', 'BEGIN', 'END', 'VAR', 'CONST', 'PROCEDURE',
            'IF', 'THEN', 'ELSE', 'WHILE', 'DO', 'FOR', 'TO',
            'INTEGER', 'REAL', 'STRING', 'ARRAY', 'OF'
        ]
        
        # Configure tag styles
        self.editor.tag_configure('keyword', foreground=self.colors['keyword_fg'], font=('Consolas', 11, 'bold'))
        self.editor.tag_configure('string', foreground=self.colors['string_fg'])
        self.editor.tag_configure('comment', foreground=self.colors['comment_fg'], font=('Consolas', 11, 'italic'))
        self.editor.tag_configure('number', foreground=self.colors['number_fg'])
        self.editor.tag_configure('operator', foreground='#dcdcaa')
        
        # Apply highlighting
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line_start = f"{i+1}.0"
            
            # Highlight keywords
            for keyword in keywords:
                start = 0
                while True:
                    pos = line.upper().find(keyword, start)
                    if pos == -1:
                        break
                    # Check if it's a whole word
                    if (pos == 0 or not line[pos-1].isalnum()) and \
                       (pos + len(keyword) >= len(line) or not line[pos + len(keyword)].isalnum()):
                        start_pos = f"{i+1}.{pos}"
                        end_pos = f"{i+1}.{pos + len(keyword)}"
                        self.editor.tag_add('keyword', start_pos, end_pos)
                    start = pos + 1
            
            # Highlight strings
            in_string = False
            start_pos = 0
            for j, char in enumerate(line):
                if char == '"' and not in_string:
                    in_string = True
                    start_pos = j
                elif char == '"' and in_string:
                    in_string = False
                    self.editor.tag_add('string', f"{i+1}.{start_pos}", f"{i+1}.{j+1}")
            
            # Highlight numbers
            import re
            for match in re.finditer(r'\b\d+\.?\d*\b', line):
                start_pos = f"{i+1}.{match.start()}"
                end_pos = f"{i+1}.{match.end()}"
                self.editor.tag_add('number', start_pos, end_pos)
            
            # Highlight operators
            operators = ['+', '-', '*', '/', ':=', '=', '#', '<', '>', '<=', '>=']
            for op in operators:
                start = 0
                while True:
                    pos = line.find(op, start)
                    if pos == -1:
                        break
                    start_pos = f"{i+1}.{pos}"
                    end_pos = f"{i+1}.{pos + len(op)}"
                    self.editor.tag_add('operator', start_pos, end_pos)
                    start = pos + 1
    
    def new_file(self):
        """Create a new file"""
        if self.current_file:
            if messagebox.askyesno("Save Changes", "Do you want to save the current file?"):
                self.save_file()
        
        self.editor.delete(1.0, tk.END)
        self.current_file = None
        self.status_label.config(text="New file")
        self.clear_output()
    
    def open_file(self):
        """Open a file"""
        filename = filedialog.askopenfilename(
            title="Open Oberon File",
            filetypes=[("Oberon files", "*.oberon"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.editor.delete(1.0, tk.END)
                self.editor.insert(1.0, content)
                self.current_file = filename
                self.status_label.config(text=f"Opened: {os.path.basename(filename)}")
                self.apply_syntax_highlighting()
                self.clear_output()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            try:
                content = self.editor.get(1.0, tk.END)
                with open(self.current_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.status_label.config(text=f"Saved: {os.path.basename(self.current_file)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        """Save the file with a new name"""
        filename = filedialog.asksaveasfilename(
            title="Save Oberon File",
            defaultextension=".oberon",
            filetypes=[("Oberon files", "*.oberon"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                content = self.editor.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_file = filename
                self.status_label.config(text=f"Saved: {os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file: {e}")
    
    def compile_code(self, on_finished=None):
        """Compile the current code. If `on_finished` is provided and compilation succeeds,
        the callable will be invoked on the main thread after compilation finishes.
        """
        if self.is_compiling:
            return

        # store optional callback to run on successful compilation
        self._compile_callback = on_finished

        self.is_compiling = True
        self.progress.start()
        self.status_label.config(text="Compiling...")

        # Run compilation in a separate thread
        thread = threading.Thread(target=self._compile_thread)
        thread.daemon = True
        thread.start()
    
    def _compile_thread(self):
        """Compilation thread"""
        try:
            source = self.editor.get(1.0, tk.END)
            
            # Clear previous output
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            
            # Compile the code (now generates native executable)
            import tempfile
            import os
            
            # Create a temporary file for source
            with tempfile.NamedTemporaryFile(mode='w', suffix='.oberon', delete=False, encoding='utf-8') as tmp:
                tmp.write(source)
                tmp_path = tmp.name
            
            try:
                messages, exe_path = self.compiler.compile_file(tmp_path, build_native=True)
                self._last_exe_path = exe_path  # Store for running
                
                # Display results
                self.root.after(0, self._display_compilation_results, messages)
                
                # record whether compilation had errors
                has_errors = any("error" in msg.lower() or "Error" in msg for msg in messages) or not exe_path
                self._last_compile_has_errors = has_errors
                
                # if compilation succeeded and a callback was provided, invoke it on main thread
                if not has_errors and getattr(self, '_compile_callback', None):
                    cb = self._compile_callback
                    self.root.after(0, cb)
            finally:
                # Clean up temp file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
        except Exception as e:
            self.root.after(0, self._display_error, f"Compilation error: {e}")
        finally:
            self.root.after(0, self._compilation_finished)
    
    def _display_compilation_results(self, output):
        """Display compilation results"""
        self.output_text.config(state=tk.NORMAL)
        
        # output je list zpráv z kompilátoru
        if not output:
            self.output_text.insert(tk.END, "No output from compiler\n", 'error')
        else:
            # Zobraz všechny zprávy
            for line in output:
                # Zkontroluj, jestli jde o chybu
                if any(keyword in line.lower() for keyword in ["error", "failed"]):
                    self.output_text.insert(tk.END, line + "\n", 'error')
                else:
                    self.output_text.insert(tk.END, line + "\n", 'success')
        
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def _display_error(self, error_msg):
        """Display error message"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.insert(tk.END, error_msg + "\n", 'error')
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def _compilation_finished(self):
        """Called when compilation is finished"""
        self.is_compiling = False
        self.progress.stop()
        self.status_label.config(text="Ready")
    
    def run_code(self):
        """Run the current code"""
        if self.is_compiling:
            return
        
        self.is_compiling = True
        self.progress.start()
        self.status_label.config(text="Running...")
        
        # Run in a separate thread
        thread = threading.Thread(target=self._run_thread)
        thread.daemon = True
        thread.start()
    
    def _run_thread(self):
        """Execution thread - compiles and runs the compiled executable"""
        try:
            source = self.editor.get(1.0, tk.END)
            
            # Clear previous output
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            
            # Compile to native executable
            import tempfile
            import os
            import subprocess
            
            # Create a temporary file for source
            with tempfile.NamedTemporaryFile(mode='w', suffix='.oberon', delete=False, encoding='utf-8') as tmp:
                tmp.write(source)
                tmp_path = tmp.name
            
            try:
                messages, exe_path = self.compiler.compile_file(tmp_path, build_native=True)
                
                # Check for compilation errors
                has_errors = any("error" in msg.lower() or "Error" in msg for msg in messages) or not exe_path
                
                if has_errors:
                    # Display compilation errors
                    self.root.after(0, self._display_compilation_results, messages)
                else:
                    # Run the compiled executable
                    try:
                        proc = subprocess.run([exe_path], capture_output=True, text=True, timeout=10)
                        output_lines = proc.stdout.split('\n') if proc.stdout else []
                        
                        if proc.returncode != 0 and proc.stderr:
                            output_lines.append(f"\n[Runtime Error]\n{proc.stderr}")
                        
                        self.root.after(0, self._display_program_output, output_lines)
                        
                        # Clean up executable after running
                        try:
                            os.unlink(exe_path)
                            # Also clean up .ll file
                            ll_path = os.path.splitext(tmp_path)[0] + '.ll'
                            if os.path.exists(ll_path):
                                os.unlink(ll_path)
                        except:
                            pass
                            
                    except subprocess.TimeoutExpired:
                        self.root.after(0, self._display_error, "Program execution timed out (10s limit)")
                    except Exception as e:
                        self.root.after(0, self._display_error, f"Error running compiled program: {e}")
            finally:
                # Clean up temp source file
                try:
                    os.unlink(tmp_path)
                except:
                    pass
            
        except Exception as e:
            self.root.after(0, self._display_error, f"Runtime error: {e}")
        finally:
            self.root.after(0, self._compilation_finished)
    
    def _display_program_output(self, output):
        """Display program output"""
        self.output_text.config(state=tk.NORMAL)
        
        self.output_text.insert(tk.END, "=== Program Output ===\n", 'success')
        for line in output:
            self.output_text.insert(tk.END, line + "\n")
        
        self.output_text.config(state=tk.DISABLED)
        self.output_text.see(tk.END)
    
    def compile_and_run(self):
        """Compile and run the code"""
        # Compile, and if successful, call `run_code` automatically
        self.compile_code(on_finished=self.run_code)
    
    def clear_output(self):
        """Clear the output area"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state=tk.DISABLED)
    
    def show_examples(self):
        """Show example code dialog"""
        examples_window = tk.Toplevel(self.root)
        examples_window.title("Oberon Examples")
        examples_window.geometry("600x400")
        examples_window.configure(bg='#f0f0f0')
        
        # Create notebook for different examples
        notebook = ttk.Notebook(examples_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load examples from examples directory
        examples_dir = "examples"
        texts = []
        
        if os.path.exists(examples_dir):
            example_files = [f for f in os.listdir(examples_dir) if f.endswith('.oberon')]
            example_files.sort()  # Sort alphabetically
            
            for file in example_files:
                name = file.replace('.oberon', '').replace('_', ' ').title()
                frame = ttk.Frame(notebook)
                notebook.add(frame, text=name)
                
                text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Consolas', 10))
                text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
                
                try:
                    with open(os.path.join(examples_dir, file), 'r', encoding='utf-8') as f:
                        content = f.read()
                    text.insert(1.0, content)
                except:
                    text.insert(1.0, f"Could not load {file}")
                
                texts.append(text)
        else:
            # Fallback if examples directory doesn't exist
            frame = ttk.Frame(notebook)
            notebook.add(frame, text="No Examples")
            text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=('Consolas', 10))
            text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            text.insert(1.0, "Examples directory not found.")
            texts.append(text)
        
        # Buttons
        button_frame = ttk.Frame(examples_window)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        def load_example():
            # Get the currently selected tab
            current_tab = notebook.select()
            tab_index = notebook.index(current_tab)
            
            content = texts[tab_index].get(1.0, tk.END)
            
            # Load into main editor
            self.editor.delete(1.0, tk.END)
            self.editor.insert(1.0, content)
            self.apply_syntax_highlighting()
            examples_window.destroy()
        
        def copy_example():
            # Get the currently selected tab
            current_tab = notebook.select()
            tab_index = notebook.index(current_tab)
            
            content = texts[tab_index].get(1.0, tk.END)
            
            # Copy to clipboard
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
        
        ttk.Button(button_frame, text="Load Example", command=load_example).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Copy Example", command=copy_example).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close", command=examples_window.destroy).pack(side=tk.RIGHT)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Oberon Compiler IDE

A modern graphical interface for the Oberon programming language compiler.

Features:
• Syntax highlighting
• Real-time compilation
• Interactive execution
• File operations
• Example code templates

Built with Python and Tkinter."""
        
        messagebox.showinfo("About", about_text)
    
    def show_syntax_help(self):
        """Show syntax help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Oberon Syntax Help")
        help_window.geometry("700x500")
        help_window.configure(bg='#f0f0f0')
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Consolas', 10))
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        syntax_help = """Oberon Language Syntax Reference

PROGRAM STRUCTURE:
MODULE ModuleName;
    [declarations]
BEGIN
    [statements]
END ModuleName.

DECLARATIONS:
CONST
    name = value;

VAR
    name: type;
    name1, name2: type;

PROCEDURE name(parameters): return_type;
    [local declarations]
BEGIN
    [statements]
END name;

DATA TYPES:
• INTEGER - whole numbers
• REAL - floating point numbers  
• STRING - text strings
• ARRAY [size] OF type - arrays

STATEMENTS:
• Assignment: variable := expression;
• Procedure call: ProcedureName(arguments);
• If statement: IF condition THEN statement [ELSE statement] END;
• While loop: WHILE condition DO statement END;
• For loop: FOR variable := start TO end DO statement END;
• Compound: BEGIN statement1; statement2; ... END;

EXPRESSIONS:
• Arithmetic: +, -, *, /, DIV, MOD
• Comparison: =, #, <, >, <=, >=
• Logical: AND, OR
• Unary: +, -

BUILT-IN PROCEDURES:
• Write(value) - output without newline
• WriteLn() - output newline

EXAMPLES:
MODULE Example;
VAR x: INTEGER;
BEGIN
    x := 42;
    Write("Value: ");
    Write(x);
    WriteLn();
END Example."""
        
        help_text.insert(1.0, syntax_help)
        help_text.config(state=tk.DISABLED)
    
    def cut_text(self):
        """Cut selected text"""
        try:
            self.editor.event_generate("<<Cut>>")
        except:
            # Fallback: manually handle cut
            if self.editor.selection_get():
                self.copy_text()
                self.editor.delete(tk.SEL_FIRST, tk.SEL_LAST)
    
    def copy_text(self):
        """Copy selected text"""
        try:
            self.editor.event_generate("<<Copy>>")
        except:
            # Fallback: manually handle copy
            if self.editor.selection_get():
                self.root.clipboard_clear()
                self.root.clipboard_append(self.editor.selection_get())
    
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.editor.event_generate("<<Paste>>")
        except:
            # Fallback: manually handle paste
            try:
                clipboard_text = self.root.clipboard_get()
                self.editor.insert(tk.INSERT, clipboard_text)
            except:
                pass  # Clipboard might be empty or not accessible
    
    def select_all_text(self):
        """Select all text in the editor"""
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)
        return "break"
    
    def on_tab_press(self, event):
        """Handle tab key press for proper indentation"""
        # Insert 4 spaces instead of tab
        self.editor.insert(tk.INSERT, "    ")
        return "break"  # Prevent default tab behavior

def main():
    """Main entry point for the GUI application"""
    root = tk.Tk()
    app = OberonGUI(root)
    
    # Configure output text tags for colored output
    app.output_text.tag_configure('success', foreground=app.colors['success_fg'])
    app.output_text.tag_configure('error', foreground=app.colors['error_fg'])
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
