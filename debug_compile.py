from compiler import Compiler

c = Compiler()
messages, exe = c.compile_file('test_proc.oberon')
for msg in messages:
    print(msg)
