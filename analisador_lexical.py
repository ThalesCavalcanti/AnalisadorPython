"""
 - identificadores: (a-z | A-Z | _)(a-z | A-Z | _ | 0-9)*
 - operadores aritméticos: + - * /
 - atribuição: =
 - relacionais: > >= < <= != ==
 - parênteses: ( )
 - constantes numéricas: 123, 123.456, .456  (não aceita 1.  or 12.)
 - palavras reservadas: int, float, print, if, else
 - comentários: linha (# até fim de linha) e bloco (/* ... */)
 - erro léxico com linha e coluna
"""

from dataclasses import dataclass
from typing import Optional, List
import string

class LexicalError(Exception):
    def __init__(self, message, line, column, char=None):
        self.message = message
        self.line = line
        self.column = column
        self.char = char
        super().__init__(f"{message} at line {line}, column {column}{(' (char: '+repr(char)+')') if char else ''}")

@dataclass
class Token:
    type: str
    value: Optional[str]
    line: int
    column: int
    def __repr__(self):
        return f"Token({self.type!r}, {self.value!r}, line={self.line}, col={self.column})"

class Lexer:
    # tabela de palavras reservadas
    # tabela de palavras reservadas
    RESERVED = {
        # tipos
        'int': 'INT',
        'float': 'FLOAT',

        # comandos e estruturas do programa
        'inicio': 'INICIO',
        'decls': 'DECLS',
        'fimdecls': 'FIMDECLS',
        'codigo': 'CODIGO',
        'fimprog': 'FIMPROG',

        # entrada e saída
        'leia': 'LEIA',
        'escreva': 'ESCREVA',

        # controle de fluxo
        'se': 'SE',
        'entao': 'ENTAO',
        'bloco': 'BLOCO',
        'fimbloco': 'FIMBLOCO',

        # operadores lógicos
        'e': 'E',
        'ou': 'OU',

        # funções e outras palavras (opcional)
        'print': 'PRINT',
        'while': 'WHILE',
        'else': 'ELSE'
    }


    def __init__(self, text: str):
        # normaliza quebras de linha para facilitar contagem
        self.text = text.replace('\r\n', '\n').replace('\r', '\n')
        self.pos = 0
        self.length = len(self.text)
        self.current_char = self.text[0] if self.text else None
        self.line = 1
        self.col = 1

    def advance(self):
        # atualiza ponteiro, linha e coluna
        if self.current_char == '\n':
            self.line += 1
            self.col = 0
        self.pos += 1
        if self.pos >= self.length:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]
            self.col += 1

    def peek(self, n=1) -> Optional[str]:
        peek_pos = self.pos + n
        if peek_pos >= self.length:
            return None
        return self.text[peek_pos]

    def peek_next_non_whitespace(self):
        pos = self.pos
        while pos < self.length and self.text[pos] in ' \t\n':
            pos += 1
        if pos < self.length:
            return self.text[pos]
        return None

    def error(self, message, char=None, line=None, col=None):
        raise LexicalError(message, line or self.line, col or self.col, char)

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char in ' \t\n':
            self.advance()

    def skip_line_comment(self):
        # ignora até o fim da linha (EOF)
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    def skip_block_comment(self):
        # consome '/*' e ignora até '*/' (gera erro se EOF)
        start_line, start_col = self.line, self.col
        # consumir '/' e '*'
        self.advance()
        self.advance()
        while self.current_char is not None:
            if self.current_char == '*' and self.peek() == '/':
                self.advance()  # '*'
                self.advance()  # '/'
                return
            self.advance()
        self.error("Unterminated block comment", None, start_line, start_col)

    def number(self) -> Token:
        start_line, start_col = self.line, self.col
        num_str = ''
        # se começar por ponto, tem que vir dígito depois (ex: .456)
        if self.current_char == '.':
            num_str += '.'
            self.advance()
            if self.current_char is None or not ('0' <= self.current_char <= '9'):
                self.error("Invalid numeric constant: '.' not followed by digits", '.', start_line, start_col)
            while self.current_char is not None and '0' <= self.current_char <= '9':
                num_str += self.current_char
                self.advance()
            return Token('NUMBER', num_str, start_line, start_col)
        # caso normal: começa com dígito
        while self.current_char is not None and '0' <= self.current_char <= '9':
            num_str += self.current_char
            self.advance()
        # parte fracionária opcional, se existir ponto deve haver ao menos um dígito depois
        if self.current_char == '.':
            num_str += '.'
            self.advance()
            if self.current_char is None or not ('0' <= self.current_char <= '9'):
                self.error("Invalid numeric constant: digits required after decimal point", '.', start_line, start_col)
            while self.current_char is not None and '0' <= self.current_char <= '9':
                num_str += self.current_char
                self.advance()
        #segundo ponto
        if self.current_char == ".":
            self.error("Invalid numeric constant: multiple decimal points", '.')
        return Token('NUMBER', num_str, start_line, start_col)

    def identifier_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.col
        result = ''
        # primeiro caractere deve ser letra ASCII ou underscore
        if self.current_char is None:
            self.error("Unexpected end while parsing identifier", None, start_line, start_col)
        if self.current_char not in string.ascii_letters and self.current_char != '_':
            self.error("Identifiers must start with ASCII letter or underscore", self.current_char, start_line, start_col)
        while self.current_char is not None and (self.current_char in string.ascii_letters or self.current_char == '_' or ('0' <= self.current_char <= '9')):
            result += self.current_char
            self.advance()
        typ = self.RESERVED.get(result.lower(), 'IDENTIFIER') 
        return Token(typ, result, start_line, start_col)


    def get_next_token(self) -> Token:
        while self.current_char is not None:
            # espaços e quebras
            if self.current_char in ' \t\n':
                self.skip_whitespace()
                continue
            # comentários
            if self.current_char == '#':
                self.skip_line_comment()
                continue
            if self.current_char == '/' and self.peek() == '*':
                self.skip_block_comment()
                continue
            # operadores aritméticos
            if self.current_char == '+':
                t = Token('PLUS', '+', self.line, self.col)
                self.advance()
                return t
            if self.current_char == '-':
                t = Token('MINUS', '-', self.line, self.col)
                self.advance()
                return t
            if self.current_char == '*':
                t = Token('MUL', '*', self.line, self.col)
                self.advance()
                return t
            if self.current_char == '/':
                # divisão 
                t = Token('DIV', '/', self.line, self.col)
                self.advance()
                return t
            # parênteses
            if self.current_char == '(':
                t = Token('LPAREN', '(', self.line, self.col)
                self.advance()
                return t
            if self.current_char == ')':
                t = Token('RPAREN', ')', self.line, self.col)
                self.advance()
                return t
            # relacionais e atribuição 
            if self.current_char == '>':
                start_line, start_col = self.line, self.col
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token('GE', '>=', start_line, start_col)
                else:
                    self.advance()
                    return Token('GT', '>', start_line, start_col)
            if self.current_char == '<':
                start_line, start_col = self.line, self.col
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token('LE', '<=', start_line, start_col)
                else:
                    self.advance()
                    return Token('LT', '<', start_line, start_col)
            if self.current_char == '!':
                start_line, start_col = self.line, self.col
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token('NE', '!=', start_line, start_col)
                else:
                    self.error("Unexpected '!' (expected '!=')", '!', start_line, start_col)
            if self.current_char == '=':
                start_line, start_col = self.line, self.col
                if self.peek() == '=':
                    self.advance(); self.advance()
                    return Token('EQ', '==', start_line, start_col)
                else:
                    self.advance()
                    return Token('ASSIGN', '=', start_line, start_col)
            # números inteiros ou com parte decimal
            if ('0' <= self.current_char <= '9') or (self.current_char == '.' and self.peek() is not None and '0' <= self.peek() <= '9'):
                token = self.number()
                # Check for '.' after number (possibly after whitespace)
                next_char = self.peek_next_non_whitespace()
                if next_char == '.':
                    self.error("Invalid numeric constant: unexpected '.' after number", '.', token.line, token.column)
                return token
            # identificadores / palavras reservadas
            if self.current_char in string.ascii_letters or self.current_char == '_':
                return self.identifier_or_keyword()
            # dois pontos usados em indetificadores
            if self.current_char == ':':
                t = Token('COLON', ':', self.line, self.col)
                self.advance()
                return t
            # caractere inválido
            self.error("Invalid character", self.current_char, self.line, self.col)
        return Token('EOF', None, self.line, self.col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            tok = self.get_next_token()
            tokens.append(tok)
            if tok.type == 'EOF':
                break
        return tokens
