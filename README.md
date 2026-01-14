# Oberonsky Kompajler

Kompajler pro podmnozinu programovacího jazyka Oberon. Implementován v Pythonu s GCC backendem pro nativní kompilaci.

## Struktura Projektu

```
interpretator/
├── output/              # Vygenerovane C soubory a spustitelne programy
├── examples/            # Prikladove Oberon programy
├── compiler.py          # Hlavni orchestrace kompajleru
├── lexer.py             # Tokenizace
├── parser.py            # Parser
├── oberon_ast.py        # Definice abstraktniho syntaktickeho stromu
├── semantic_analyzer.py # Semanticka analyza
├── c_emitter.py         # Generator C kodu
├── interpreter.py       # Nahradvny Python interpreter
├── gui.py               # Tkinter IDE
└── README.md            # Tento soubor
```

Vsechny vygenerovane C soubory (.c) a spustitelne programy (.exe) jsou automaticky umisteny do slozky `output/`.

## Rychly Start

### Pouziti GUI

```bash
python gui.py
```

Spusti Tkinter IDE kde muzes:
- Psat nebo vlozit Oberon kod
- Kompajlovat na nativni spustitelny program (GCC backend)
- Spoustet programy s integrovanym zobrazenim vystupu
- Nacitat prikladove programy

### Kompajlovani z Prikazoveho Radku

```bash
python compiler.py examples/hello_world.oberon
```

To:
1. Kompajluje Oberon kod na C (`output/hello_world.c`)
2. Kompajluje C na nativni spustitelny program (`output/hello_world.exe`)
3. Vraci cestu k spustitelnemu programu

### Programovane Pouziti

```python
from compiler import Compiler

compiler = Compiler()  # Pouziva 'output/' slozku
messages, exe_path = compiler.compile_source(oberon_code, source_filename='myprogram')

if exe_path:
    print(f"Spustitelny program vytvoren: {exe_path}")
```

## Podporovane Prvky

### Datove Typy
- `INTEGER` - 32-bitova cela cisla
- `REAL` - Cisla s plovajici carkou
- `STRING` - Textove retezce
- `ARRAY` - Jednorozmerná a vicerozmerná pole

### Struktura Programu
```oberon
MODULE ProgramName;
  VAR x: INTEGER;
BEGIN
  x := 42;
  Write(x);
END ProgramName.
```

### Procedury a Funkce
```oberon
PROCEDURE Add(a, b: INTEGER): INTEGER;
BEGIN
  RETURN a + b;
END Add;
```

### Rizici Struktury
- IF-THEN-ELSE
- WHILE cykly
- FOR cykly

### Pole
```oberon
VAR arr: ARRAY 10 OF INTEGER;
BEGIN
  arr[0] := 42;
  Write(arr[0]);
END.
```

### Vicerozmerná Pole
```oberon
VAR matrix: ARRAY 3, 3 OF INTEGER;
BEGIN
  matrix[0, 1] := 5;
END.
```

## Prikladove Programy

Vsechny priklady jsou v adresar `examples/`:

| Soubor | Popis |
|--------|-------|
| hello_world.oberon | Zakladni program s vystuem |
| arithmetic.oberon | Celocisla a desitinna aritmetika |
| control_structures.oberon | IF, WHILE, FOR prikazy |
| procedures.oberon | Definice a volani procedur |
| arrays.oberon | Jednorozmerná pole |
| arrays_2d.oberon | Dvourozmerná pole |
| multidimensional_arrays.oberon | N-rozmerná pole |
| indirect_recursion.oberon | Vzajemna rekurze |
| nested_procedures.oberon | Procedury v procedurah |
| types_conversions.oberon | Manipulace s typy |

## Spusteni Programu

```bash
# Hello World
python compiler.py examples/hello_world.oberon

# Aritmetika
python compiler.py examples/arithmetic.oberon

# Rizici struktury
python compiler.py examples/control_structures.oberon

# Procedury
python compiler.py examples/procedures.oberon

# Pole
python compiler.py examples/arrays.oberon
```

## Architektura Kompajleru

1. **Lexer** - Tokenizace zdrojoveho kodu
2. **Parser** - Vytvoreni abstraktniho syntaktickeho stromu (AST)
3. **Semanticka Analyza** - Kontrola typu a oveovani promennnych
4. **C Emitter** - Vytvoreni C kodu
5. **GCC** - Nativni kompilace na spustitelny program

## Syntaxe Jazyka

Oberon-0 podmnozina:

```oberon
MODULE Program;
  VAR x: INTEGER;
  
  PROCEDURE DoSomething(n: INTEGER): INTEGER;
  BEGIN
    RETURN n * 2;
  END DoSomething;
  
BEGIN
  x := 42;
  Write(DoSomething(x));
  WriteLn();
END Program.
```

## Operatory

Aritmeticke: `+`, `-`, `*`, `/`, `DIV`, `MOD`
Relacni: `=`, `#`, `<`, `>`, `<=`, `>=`
Logicke: `AND`, `OR`

## Vstavene Procedury

- `Write(value)` - Vypis hodnoty
- `WriteLn()` - Vypis noveho radku

## Pozadavky

- Python 3.10+
- GCC (pro nativni kompilaci)

## Testovani

Vsech 12 prikladovych programu pracuje bez problemu.
