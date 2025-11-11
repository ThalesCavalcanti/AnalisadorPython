# Analisador Léxico e Sintático em Python

Este projeto implementa um **analisador léxico manual** em Python, sem uso de ferramentas automáticas (como Lex ou PLY).
O analisador percorre o código fonte caractere por caractere e gera **tokens** de acordo com regras definidas.

## Funcionalidades

* **Identificadores**
  `(a-z | A-Z | _)(a-z | A-Z | _ | 0-9)*`

* **Operadores aritméticos**
  `+` `-` `*` `/`

* **Operador de atribuição**
  `=`

* **Operadores relacionais**
  `>` `>=` `<` `<=` `!=` `==`

* **Parênteses**
  `(` `)`

* **Constantes numéricas**

  * Inteiros: `123`
  * Reais: `123.456`, `.456`
  * Inválidos: `1.`, `12.`, `156.`

* **Palavras reservadas**
  `int`, `float`, `print`, `if`, `else`

* **Comentários**

  * Linha única: `# comentário até o fim da linha`
  * Bloco: `/* comentário em várias linhas */`

* **Erros léxicos**
  Geração de mensagens de erro indicando linha, coluna e caractere inválido encontrado.

## Estrutura do Código

* `Token`: representa cada unidade léxica reconhecida.
* `LexicalError`: exceção personalizada para erros léxicos.
* `Lexer`: classe principal do analisador léxico.

  * Ignora espaços e comentários.
  * Reconhece tokens conforme regras.
  * Gera erros em caso de entrada inválida.

## Exemplo de Uso

```python
from analisador_lexico import Lexer, LexicalError

codigo = """
int a = 123
float b = 123.456
print(a + b * (a - .456) / 2)
if a >= b
else a = a == b
"""

lexer = Lexer(codigo)
try:
    tokens = lexer.tokenize()
    for token in tokens:
        print(token)
except LexicalError as e:
    print("Erro léxico:", e)
```

### Saída Esperada

```
Token('INT', 'int', line=2, col=1)
Token('IDENTIFIER', 'a', line=2, col=5)
Token('ASSIGN', '=', line=2, col=7)
Token('NUMBER', '123', line=2, col=9)
...
Token('EOF', None, line=7, col=15)
```

## Como Executar

1. Clone o repositório:

   ```bash
   git clone https://github.com/seu-usuario/analisador-lexico.git
   cd analisador-lexico
   ```

2. Execute o analisador com o exemplo embutido:

   ```bash
   python analisador_lexico.py
   ```

3. Importe a classe `Lexer` em seus próprios projetos.

## Requisitos

* Python 3.7 ou superior
* graphviz (pip install graphviz || sudo apt install graphviz)

## Membros

* Thales Alexandre Dos Santos Cavalcanti
* Sâmi Gabriele De Andrade Carvalho
* Ygor Vinnicius Rodrigues de Pontes
* Lauane Louise Viana Santos 
