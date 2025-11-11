from analisador_lexical import Lexer, LexicalError
from analisador_sintatico import Parser, SyntaxError_

def main():
    filename = "programa.mc"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            src = f.read()
    except FileNotFoundError:
        print(f"Arquivo '{filename}' não encontrado.")
        return

    try:
        lexer = Lexer(src)
        parser = Parser(lexer)
        parser.parse_programa()
    except LexicalError as e:
        print(f"Erro léxico: {e}")
    except SyntaxError_ as e:
        print(f"{e}")

if __name__ == "__main__":
    main()
