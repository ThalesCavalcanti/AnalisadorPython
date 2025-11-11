# analisador_sintatico.py
from analisador_lexical import Lexer, LexicalError, Token
from graphviz import Digraph

class SyntaxError_(Exception):
    def __init__(self, message, token):
        msg = f"Erro sintático: {message} perto de '{token.value}' (linha {token.line}, coluna {token.column})"
        super().__init__(msg)

class Node:
    """Representa um nó da árvore sintática."""
    def __init__(self, label):
        self.label = label
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class Parser:
    def __init__(self, lexer: Lexer):
        self.tokens = lexer.tokenize()
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.node_counter = 0
        self.graph = Digraph(comment="Árvore Sintática")
        self.graph.attr("node", shape="ellipse", style="filled", color="lightgrey", fontname="Arial")


    # Funções utilitárias

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]

    def eat(self, token_type):
        if self.current_token.type == token_type:
            node = Node(f"{token_type}({self.current_token.value})" if self.current_token.value else token_type)
            self.advance()
            return node
        else:
            raise SyntaxError_(f"Esperado {token_type}, encontrado {self.current_token.type}", self.current_token)

    def peek_next_type(self, offset=1):
        """Retorna o tipo do token `offset` posições à frente (ou None)."""
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx].type
        return None


    # Regras gramaticais

    def parse_programa(self):
        root = Node("Programa")

        root.add_child(self.eat("INICIO"))
        root.add_child(self.eat("DECLS"))
        root.add_child(self.parse_decls())
        root.add_child(self.eat("FIMDECLS"))
        root.add_child(self.eat("CODIGO"))
        root.add_child(self.parse_comandos())
        root.add_child(self.eat("FIMPROG"))

        self._build_graph(root)
        self.graph.render("arvore_sintatica", format="png", cleanup=True)
        print("Programa sintaticamente correto. Grafo gerado: arvore_sintatica.png")
        return root


    # Declarações

    def peek_is_colon(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1].type == 'COLON'
        return False

    def parse_decls(self):
        node = Node("Decls")
        while self.current_token.type not in ("FIMDECLS", "EOF"):
            if self.current_token.type == "IDENTIFIER" and self.peek_is_colon():
                node.add_child(self.parse_decl())
            else:
                raise SyntaxError_("Esperado declaração de variável no formato 'nome:TIPO' ou 'FIMDECLS' para terminar DECLS", self.current_token)
        return node

    def parse_decl(self):
        node = Node("Decl")
        node.add_child(self.eat("IDENTIFIER"))
        node.add_child(self.eat("COLON"))

        if self.current_token.type in ("INT", "FLOAT"):
            node.add_child(self.eat(self.current_token.type))
        else:
            raise SyntaxError_("Tipo esperado (INT ou FLOAT) após ':' na declaração", self.current_token)
        return node


    # Bloco de comandos

    def parse_comandos(self):
        node = Node("Comandos")
        while self.current_token.type not in ("FIMPROG", "FIMBLOCO", "FIMDECLS", "EOF"):
            node.add_child(self.parse_comando())
        return node

    def parse_comando(self):
        node = Node("Comando")
        ttype = self.current_token.type

        if ttype == "LEIA":
            node.add_child(self.eat("LEIA"))
            node.add_child(self.eat("IDENTIFIER"))

        elif ttype == "ESCREVA":
            node.add_child(self.eat("ESCREVA"))
            node.add_child(self.eat("LPAREN"))
            if self.current_token.type in ("IDENTIFIER", "NUMBER"):
                node.add_child(self.eat(self.current_token.type))
            else:
                raise SyntaxError_("Esperado identificador ou número dentro de ESCREVA(...)", self.current_token)
            node.add_child(self.eat("RPAREN"))

        elif ttype == "SE":
            node.add_child(self.parse_if())

        elif ttype == "IDENTIFIER":
            # Verifica se é atribuição válida (IDENTIFIER seguido de ASSIGN)
            next_type = self.peek_next_type()
            if next_type == "ASSIGN":
                node.add_child(self.parse_atribuicao())
            else:
                raise SyntaxError_(
                    f"Esperado '=' (ASSIGN) após identificador no início do comando, encontrado {next_type}",
                    self.current_token
                )

        else:
            raise SyntaxError_("Comando inválido", self.current_token)

        return node


    # Atribuições

    def parse_atribuicao(self):
        node = Node("Atribuicao")
        node.add_child(self.eat("IDENTIFIER"))
        node.add_child(self.eat("ASSIGN"))
        node.add_child(self.parse_expressao_logica())
        return node

 
    # Estruturas condicionais

    def parse_if(self):
        node = Node("Condicional")
        node.add_child(self.eat("SE"))
        node.add_child(self.parse_expressao_logica())
        node.add_child(self.eat("ENTAO"))
        node.add_child(self.eat("BLOCO"))
        node.add_child(self.parse_comandos())
        node.add_child(self.eat("FIMBLOCO"))
        return node


    # EXPRESSÕES — com operadores lógicos

    def parse_expressao_logica(self):
        """expressao_logica ::= expressao_relacional ( (E|OU) expressao_relacional )*"""
        node = Node("ExpressaoLogica")
        node.add_child(self.parse_expressao_relacional())

        while self.current_token.type in ("E", "OU"):
            op = Node(self.current_token.type)
            self.advance()
            op.add_child(node.children.pop())
            op.add_child(self.parse_expressao_relacional())
            node.add_child(op)

        return node

    def parse_expressao_relacional(self):
        """expressao_relacional ::= expressao_aritmetica (relop expressao_aritmetica)?"""
        node = Node("ExpressaoRelacional")
        node.add_child(self.parse_expressao_aritmetica())

        if self.current_token.type in ("GT", "LT", "GE", "LE", "EQ", "NE"):
            op = Node(self.current_token.value)
            self.advance()
            op.add_child(node.children.pop())
            op.add_child(self.parse_expressao_aritmetica())
            node.add_child(op)

        return node

    def parse_expressao_aritmetica(self):
        """expressao_aritmetica ::= termo ((PLUS|MINUS) termo)*"""
        node = Node("ExpressaoAritmetica")
        node.add_child(self.parse_termo())

        while self.current_token.type in ("PLUS", "MINUS"):
            op = Node(self.current_token.value)
            self.advance()
            op.add_child(node.children.pop())
            op.add_child(self.parse_termo())
            node.add_child(op)

        return node

    def parse_termo(self):
        node = Node("Termo")
        node.add_child(self.parse_fator())
        while self.current_token.type in ("MUL", "DIV"):
            op = Node(self.current_token.value)
            self.advance()
            op.add_child(node.children.pop())
            op.add_child(self.parse_fator())
            node.add_child(op)
        return node

    def parse_fator(self):
        if self.current_token.type in ("NUMBER", "IDENTIFIER"):
            node = Node(f"{self.current_token.type}({self.current_token.value})")
            self.advance()
            return node
        elif self.current_token.type == "LPAREN":
            node = Node("Group")
            node.add_child(self.eat("LPAREN"))
            node.add_child(self.parse_expressao_logica())
            node.add_child(self.eat("RPAREN"))
            return node
        else:
            raise SyntaxError_("Fator inesperado na expressão", self.current_token)


    # GERAÇÃO DO GRAFO

    def _build_graph(self, node, parent_id=None):
        node_id = str(self.node_counter)
        self.node_counter += 1
        self.graph.node(node_id, label=node.label)

        if parent_id is not None:
            self.graph.edge(parent_id, node_id)

        for child in node.children:
            self._build_graph(child, node_id)