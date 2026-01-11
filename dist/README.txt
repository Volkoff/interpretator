dir *.oberon
# Oberon Compiler - Distribuce

Tento balík obsahuje samostatný spustitelný soubor Oberon kompilátoru pro Windows.

Co obsahuje:
- `oberon.exe` (samostatný spustitelný soubor s GUI a příkazovým rozhraním)
- `examples/` (složka s příklady)
- `README.txt` (tento soubor)

Rychlý start:

- Spustit GUI (doporučeno, přes cmd):

```
oberon.exe -g
```

- Spustit program z příkazové řádky:

```
oberon.exe examples/hello_world.oberon
```

Základní příkazy:

- `oberon.exe -h`  Zobrazí nápovědu
- `oberon.exe -v`  Zobrazí verzi
- `oberon.exe -g`  Spustí interaktivní IDE
- `oberon.exe <soubor.oberon>`  Spustí nebo zkompiluje program
- `oberon.exe <soubor.oberon> -c`  Vygeneruje LLVM IR (.ll)

Instalace:

1. Rozbalte obsah archivu do složky.
2. Spusťte `oberon.exe -g` nebo spusťte konkrétní soubor `oberon.exe my.oberon`.
3. (Volitelné) Zkopírujte `oberon.exe` do `C:\Program Files\Oberon\` a přidejte do PATH.

Použití GUI:

1. Spusťte `oberon.exe -g`.
2. V editoru napište nebo načtěte Oberon kód.
3. Klikněte na tlačítko Run pro spuštění.

Podporované vlastnosti:

- Datové typy: `INTEGER`, `REAL`, `STRING`, `ARRAY` (vícedimenzionální)
- Kontrolní struktury: `IF`, `WHILE`, `FOR`
- Procedury a funkce, včetně zanořených a rekurzivních volání
- Základní standardní procedury: `Write`, `WriteLn`
- Možnost vygenerovat LLVM IR

Řešení problémů:

- Pokud GUI nelze spustit, spusťte `oberon.exe -g` z příkazové řádky a zkontrolujte chybové hlášky.
- Pokud program nenajde soubor, ověřte cestu a běžný adresář.

Požadavky systému:

- Windows 7 nebo novější (64-bit)
- Žádná samostatná instalace Pythonu není potřeba

Poznámka:

Složka `examples/` zůstává v distribučním balíku; v tomto souboru nejsou uvedeny jednotlivé příklady.

GIT REPO:
https://github.com/Volkoff/interpretator.git

