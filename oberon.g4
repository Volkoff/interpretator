grammar Oberon;

program: 'MODULE' IDENTIFIER ';' declarations 'BEGIN' statements 'END' IDENTIFIER '.' ;

declarations: (constDeclaration | varDeclaration | procedureDeclaration)* ;

constDeclaration: 'CONST' IDENTIFIER '=' expression ';' ;

varDeclaration: 'VAR' varList ';' ;

varList: IDENTIFIER (',' IDENTIFIER)* ':' type ;

type: 'INTEGER' | 'REAL' | 'STRING' | 'ARRAY' INTEGER_LITERAL 'OF' type ;

procedureDeclaration: 'PROCEDURE' IDENTIFIER '(' parameters? ')' (';' type)? ';' declarations 'BEGIN' statements 'END' IDENTIFIER ';' ;

parameters: parameter (',' parameter)* ;

parameter: IDENTIFIER ':' type ;

statements: statement (';' statement)* ;

statement: assignment | procedureCall | ifStatement | whileStatement | forStatement | compoundStatement ;

assignment: designator ':=' expression ;

designator: IDENTIFIER ('[' expression ']')? ;

procedureCall: IDENTIFIER '(' arguments? ')' ;

arguments: expression (',' expression)* ;

ifStatement: 'IF' expression 'THEN' statements ('ELSE' statements)? 'END' ;

whileStatement: 'WHILE' expression 'DO' statements 'END' ;

forStatement: 'FOR' IDENTIFIER ':=' expression 'TO' expression 'DO' statements 'END' ;

compoundStatement: 'BEGIN' statements 'END' ;

expression: simpleExpression (relation simpleExpression)? ;

relation: '=' | '#' | '<' | '<=' | '>' | '>=' ;

simpleExpression: ('+' | '-')? term (addOperator term)* ;

addOperator: '+' | '-' | 'OR' ;

term: factor (mulOperator factor)* ;

mulOperator: '*' | '/' | 'DIV' | 'MOD' | 'AND' ;

factor: designator | literal | '(' expression ')' | functionCall ;

functionCall: IDENTIFIER '(' arguments? ')' ;

literal: INTEGER_LITERAL | REAL_LITERAL | STRING_LITERAL ;

IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]* ;

INTEGER_LITERAL: [0-9]+ ;

REAL_LITERAL: [0-9]+ '.' [0-9]+ ;

STRING_LITERAL: '"' (~["])* '"' ;

WS: [ \t\r\n]+ -> skip ;

COMMENT: '(*' .*? '*)' -> skip ;