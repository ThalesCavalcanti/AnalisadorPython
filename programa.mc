INICIO DECLS
num1:INT
num2:INT
num3:INT
aux:INT
FIMDECLS

CODIGO
# Coloca 3 numeros em ordem crescente
LEIA num1
LEIA num2
LEIA num3

SE num1 > num2 ENTAO
    BLOCO
        aux = num2
        num2 = num1
        num1 = aux
    FIMBLOCO

SE num1 > num3 E num2 <= num3 E num1 > 3 OU num2 != num3 ENTAO
    BLOCO
        aux = (num3)
        num3 = num1
        num1 = aux
    FIMBLOCO
SE num2 > num3 ENTAO
    BLOCO
        aux = num3
        num3 = num2
        num2 = aux
    FIMBLOCO

ESCREVA(num1)
ESCREVA(num2)
ESCREVA(num3)
FIMPROG