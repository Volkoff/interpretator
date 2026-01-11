#!/usr/bin/env python3
import re
import os

def clean_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        if line.strip().startswith('"""'):
            if '"""' in line[4:]:
                i += 1
                continue
            else:
                end_quote_line = i + 1
                while end_quote_line < len(lines) and '"""' not in lines[end_quote_line]:
                    end_quote_line += 1
                i = end_quote_line + 1
                continue
        
        if '#' in line and not ('"""' in line or "'''" in line):
            line = line.split('#')[0].rstrip() + '\n'
        
        if line.strip() or line == '\n':
            result.append(line)
        
        i += 1
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.writelines(result)

files_to_clean = [
    'parser.py',
    'oberon_ast.py', 
    'semantic_analyzer.py',
    'interpreter.py',
    'emitter.py',
    'compiler.py',
    'gui.py'
]

for fname in files_to_clean:
    if os.path.exists(fname):
        clean_file(fname)
        print(f'Cleaned {fname}')
    else:
        print(f'File {fname} not found')

print('Done!')
