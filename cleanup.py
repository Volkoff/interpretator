import os
import re

def remove_docstrings_and_comments(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    result = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Skip module-level docstrings
        if i == 0 and line.strip().startswith('"""'):
            while i < len(lines) and (i == 0 or '"""' not in lines[i]):
                i += 1
            if i < len(lines):
                i += 1
            continue
        
        # Skip docstrings after method definitions
        if line.strip().startswith('def '):
            result.append(line)
            i += 1
            if i < len(lines) and '"""' in lines[i]:
                i += 1
                while i < len(lines) and '"""' not in lines[i]:
                    i += 1
                if i < len(lines):
                    i += 1
            continue
        
        # Remove inline comments
        if '#' in line:
            # Simple approach: remove everything after # (won't work for # in strings, but close enough)
            cleaned = line.split('#')[0].rstrip()
            if cleaned:
                result.append(cleaned)
            elif line.strip() == '':
                result.append('')
        else:
            result.append(line)
        
        i += 1
    
    cleaned_content = '\n'.join(result)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    
    print(f'Cleaned {os.path.basename(file_path)}')

for fname in ['interpreter.py', 'emitter.py', 'gui.py']:
    if os.path.exists(fname):
        remove_docstrings_and_comments(fname)

print('Done!')
