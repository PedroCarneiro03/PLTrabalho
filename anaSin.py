# ----------------------------------------------------
# Projeto final Processamento de Linguagens
# Leonardo Filipe Lima Barroso, a100894
# Miguel Ângelo Martins Guimarães, a100837
# Pedro Andrade Carneiro, a100652
# ----------------------------------------------------

# Uso do programa:
# Ir inserindo as expressões manualmente e clicando enter.
# Assim que estiverem todas inseridas fazer CTRL + D (Visual studio)
#
# Alternativamente poderá ser inserido um ficheiro atráves do comando:
# python3 anaSin.py < testFile.txt 
#
# Pode-se entrar no modo debug iniciando o programa com:
# python3 anaSin.py debug

#################################### GRAMATICA ####################################
#  cont -> cont type
#        | ε
#
#  type -> arit       -- Operações aritmeticas
#        | comment    -- Comentarios
#        | createfunc -- Definição de funções
#        | callfunc   -- Chamada de funções
#        | stack      -- Operações de stack
#        | input      -- Operações de input
#        | compare    -- Operações de comparação
#        | print      -- Operações de print
#        | cond       -- Condicionais
#        | cicle      -- Ciclos
#        | vars       -- Variaveis
#
#  ------------------------------------------------------------------------------   
#  -- Secção -- Conteudo de uma função (Uma função não pode chamar outra função)
#
#  contfunc -> contfunc cftype 
#            | ε
#
#  cftype -> arit       -- Operações aritmeticas
#          | comment    -- Comentarios
#          | callfunc   -- Chamada de funções
#          | stack      -- Operações de stack
#          | input      -- Operações de input
#          | compare    -- Operações de comparação
#          | print      -- Operações de print
#          | cond       -- Condicionais
#          | cicle      -- Ciclos
#          | vars       -- Variaveis
#
#  -------------------------------------------------------------------------------
#
#  arit -> MAIS    -- Soma 
#        | MENOS   -- Subtração 
#        | MUL     -- Multiplicação 
#        | DIV     -- Divisão 
#        | MOD     -- Resto da divisão inteira
#        | ABS     -- Retorna o absoluto do valor no topo da stack.
#        | 1SUM    -- Soma 1 ao valor no topo da stack.
#        | 1SUB    -- Subtrai 1 do valor no topo da stack.
#        | 2DIV    -- Divide o valor no topo da stack por 2.
#
#  comment -> COMMENT     -- Comentario
#           | ENDCOMMENT  -- Comentario de linha
#
#  createfunc -> COLON ID contfunc SEMICOLON  -- Definir função
#
#  callfunc -> ID  -- Chamar função
#
#  stack -> NUM        -- Inserir num na stack 
#         | CHAR       -- Inserir letra na stack 
#         | DROP       -- Retira o primeiro elem da stack
#         | DUP        -- Duplicar valor na stack
#         | SWAP       -- Da swap aos dois ultimos elems 
#         | NIP        -- Remove o segundo item da stack
#         | 2DROP      -- Remove os dois elementos no topo da stack
#         | ROT        -- Coloca o terceiro item no topo
#         | OVER       -- Faz uma copia do segundo item e coloca no topo
#         | 2DUP       -- Duplica o par no topo da stack 
#         | 2SWAP      -- Troca os dois pares no topo da stack 
#         | 2OVER      -- Copiar o 2o par no topo da stack e colar no topo da stack
#         | TUCK       -- Insere uma copia do primeiro elemento debaixo do segundo
#         | NUM PICK (DESATIVADO) -- Faz uma copia do n-esimo elemento da stack
#
#  input -> KEY        -- Recebe como input um caracter/tecla e coloca no topo da stack.
# 
#  compare -> EQ         -- Retorna verdade se os dois valores no topo da stack forem iguais.
#           | NEQ        -- Retorna verdade se os dois valores no topo da stack forem diferentes.
#           | MENOR      -- Retorna verdade se o 2 valor no topo da stack for menor que o primeiro. Nota: (Infixo: 10 < 2, Posfixo: 10 2 <).
#           | MAIOR      -- Retorna verdade se o 2 valor no topo da stack for maior que o primeiro. Nota: (Infixo: 10 > 2, Posfixo: 10 2 >).
#           | MENOREQ    -- Retorna verdade se o 2 valor no topo da stack for menor ou igual ao primeiro. Nota: (Infixo: 10 <= 2, Posfixo: 10 2 <=).
#           | MAIOREQ    -- Retorna verdade se o 2 valor no topo da stack for maior ou igual ao primeiro. Nota: (Infixo: 10 >= 2, Posfixo: 10 2 >=).
#           | ZEROEQ     -- Retorna verdade se o valor no topo da stack for igual de zero.
#           | ZERONEQ    -- Retorna verdade se o valor no topo da stack for diferente de zero.
#           | ZEROMENOR  -- Retorna verdade se o valor no topo da stack for igual ou menor que zero.
#           | ZEROMAIOR  -- Retorna verdade se o valor no topo da stack for igual ou maior que zero.
#           | NEGATE     -- Nega o numero no topo da stack.
#           | MIN        -- Retorna o menor dos dois valores no topo da stack.
#           | MAX        -- Retorna o maior dos dois valores no topo da stack.
#
#  print -> PONTO      -- Print do elemento no topo da stack
#         | EMIT       -- Dá print ao caracter na primeira posição da stack, o caracter é representado em ascii. 
#         | STRPRINT   -- Print a uma string
#         | STRPRINT2  -- Print a uma string mas remove espaços consecutivos
#         | SPACES     -- Print a uma determinada quantidade de espaços (O numero é o valor no topo da stack).
#         | SPACE      -- Print a um espaço.
#         | CR         -- Print a um new-line (\n).
#
#  cond -> IF cont ELSE cont THEN  -- Condicional com if else e then.
#        | IF cont THEN cont       -- Condicional com if e then.
#
#  cicle -> I             -- Obter valor do contador
#         | DO cont LOOP  -- Ciclo 
#
#  vars -> VARIABLE ID    -- Criação de variaveis
#        | ID FETCH       -- Obter valor de variavel
#        | ID STORE       -- Guardar o valor de variavel
#
#################################### SETUP ####################################
# Imports
from anaLex import tokens
import ply.yacc as yacc
import sys
import os
import re

# Variáveis 
global debug             # (Valor é carregado pela função tratarArgumentos)
global funcoesProtegidas # (Valor é carregado pela função carregarFuncoesProtegidas) 
global condCounter       # Contador para o numero de condições
global doCounter         # Contador para o numero de ciclos

localResultado  = "result"                # Pasta para os resultados
ficheiroFuncoes = "recursos/funcoes.txt"  # Ficheiro as funções utilizadas na vm

debug = False               # Modo debug ativo ou inativo (Inativo por predefinição)
funcs = {}                  # Armazenar o codigo das funções
funcoesProtegidas = set()   # Contém os nomes de todas as funções do sistema. Utilizado para impedir repetições.
condCounter = 0             # Contador para o numero de condições
doCounter = 0               # Contador para o numero de ciclos
vars = {}                   # Variaveis definidas pelo utilizador
numVars = 0                 # Numero de variaveis definidas pelo utilizador

# Valores hardcoded:
memSys = 7  # Numero de pushi 0 a dar antes do start 
# (A 7 posição é utilizada para saber o numero de frames para os ciclos as restantes são utilizadas nas funções do sistema)

#ficheiroStart   = "recursos/start.txt"    # Ficheiro com o inicio do codigo (NAO UTILIZADO)
#################################### BOAS-VINDAS ####################################
print(
"""-------------------------------------
Processamento de Linguagens
Engenharia Informática (3º ano)
Compilador de Forth
-------------------------------------""")

#################################### FUNÇÕES AUXILIARES ####################################
# Guardar o resultado final obtido
def guardarResultado(local, resultado):
    try:
        # Verificar se existe a pasta
        if not os.path.exists(local): os.makedirs(local)
        
        # Caminho completo para o ficheiro result.txt
        ficheiro = os.path.join(local, "result.txt")

        # Abre o arquivo em modo de escrita
        f = open(ficheiro, "w")
        f.write(resultado)

    except Exception as e:
        raise Exception("Erro ao guardar o resultado: {e}")

# Carrega o conteudo de um ficheiro
def carregarTxt(ficheiro):
    try:
        f = open(ficheiro, 'r')
        conteudo = f.read()
        return conteudo
    except FileNotFoundError:
        raise Exception(f'Ficheiro {ficheiro} não encontrado!')
    except Exception as e:
        raise Exception(f"Erro ao carregar {ficheiro}: {e}")

# Carrega os nomes de todas as funções do sistema para dentro de um conjunto
def carregarFuncProtegidas(ficheiro):
    funcStart = r'([A-Za-z_][A-Za-z_0-9]+):'
    with open(ficheiro, 'r') as file:
        texto = file.read()
        matches = re.findall(funcStart, texto)
        return set(matches)

# Trata dos argumentos passados para o programa
def tratarArgumentos(argumentos):
    global debug

    # Verificar a quantidade de argumentos recebidos
    if len(argumentos) == 2:
        # Verificar o argumento recebido
        if argumentos[1].lower() == 'debug': debug = True
        else: raise Exception("Programa: Argumento com valor desconhecido!")    
    elif len(argumentos) > 2:
        raise Exception("Programa: Demasiados argumentos!")

# Cria uma sequencia de pushi 0 dependendo do numero inserido 
def criarMemoria(mem):
    memoria = ""
    for i in range(mem):
        memoria += "PUSHI 0 \n"
    return memoria

# Cria uma sequencia de pushi 0 dependendo do numero inserido 
def criarMemoriaVars(vars):
    memoria = ""
    for var in vars:
        memoria += f"PUSHI 0 // Var {var}\n"
    return memoria

####################################  CODIGO  ####################################
# ---------------------------------- CONTEUDO ----------------------------------
# Conteudo regras
def p_cont_op(p):
    'cont : cont type'
    p[0] = p[1] + p[2]
    if(debug): print("P_cont_op")

def p_cont_empty(p):
    'cont : empty'
    p[0] = ''
    if(debug): print("P_cont_empty")

# ---------------------------------- TYPE ----------------------------------
def p_type_arit(p):
    'type : arit'
    p[0] = p[1]
    if(debug): print("P_type_arit")

def p_type_comment(p):
    'type : comment'
    p[0] = p[1]
    if(debug): print("P_type_comment")

def p_type_createfunc(p):
    'type : createfunc'
    p[0] = p[1]
    if(debug): print("P_type_createfunc")

def p_type_callfunc(p):
    'type : callfunc'
    p[0] = p[1]
    if(debug): print("P_type_callfunc")

def p_type_stack(p):
    'type : stack'
    p[0] = p[1]
    if(debug): print("P_type_stack")

def p_type_input(p):
    'type : input'
    p[0] = p[1]
    if(debug): print("P_type_input")

def p_type_compare(p):
    'type : compare'
    p[0] = p[1]
    if(debug): print("P_type_compare")

def p_type_print(p):
    'type : print'
    p[0] = p[1]
    if(debug): print("P_type_print")
    
def p_type_cond(p):
    'type : cond'
    p[0] = p[1]
    if(debug): print("P_type_cond")

def p_type_cicle(p):
    'type : cicle'
    p[0] = p[1]
    if(debug): print("P_type_cicle")

def p_type_vars(p):
    'type : vars'
    p[0] = p[1]
    if(debug): print("P_type_vars")

# ---------------------------------- CONTEUDO FUNC ----------------------------------
# Conteudo regras
def p_contfunc_op(p):
    'contfunc : contfunc cftype'
    p[0] = p[1] + p[2]
    if(debug): print("P_contfunc_op")

def p_contfunc_empty(p):
    'contfunc : empty'
    p[0] = ''
    if(debug): print("P_contfunc_empty")

# ---------------------------------- TYPE ----------------------------------
def p_cftype_arit(p):
    'cftype : arit'
    p[0] = p[1]
    if(debug): print("P_cftype_arit")

def p_cftype_comment(p):
    'cftype : comment'
    p[0] = p[1]
    if(debug): print("P_cftype_comment")

def p_cftype_callfunc(p):
    'cftype : callfunc'
    p[0] = p[1]
    if(debug): print("P_cftype_callfunc")

def p_cftype_stack(p):
    'cftype : stack'
    p[0] = p[1]
    if(debug): print("P_cftype_stack")

def p_cftype_input(p):
    'cftype : input'
    p[0] = p[1]
    if(debug): print("P_cftype_input")

def p_cftype_compare(p):
    'cftype : compare'
    p[0] = p[1]
    if(debug): print("P_cftype_compare")

def p_cftype_print(p):
    'cftype : print'
    p[0] = p[1]
    if(debug): print("P_cftype_print")
    
def p_cftype_cond(p):
    'cftype : cond'
    p[0] = p[1]
    if(debug): print("P_cftype_cond")

def p_cftype_cicle(p):
    'cftype : cicle'
    p[0] = p[1]
    if(debug): print("P_cftype_cicle")

def p_cftype_vars(p):
    'cftype : vars'
    p[0] = p[1]
    if(debug): print("P_cftype_vars")

# ----------------------------------------------------------------- ARIT -----------------------------------------------------------------
def p_arit_sum(p):
    'arit : MAIS'
    p[0] = "ADD\n"
    if(debug): print("P_arit_sum")

def p_arit_sub(p):
    'arit : MENOS'
    p[0] = "SUB\n"
    if(debug): print("P_arit_sub")

def p_arit_mul(p):
    'arit : MUL'
    p[0] = "MUL\n"
    if(debug): print("P_arit_mul")

def p_arit_div(p):
    'arit : DIV'
    p[0] = "DIV\n"
    if(debug): print("P_arit_div")

def p_arit_mod(p):
    'arit : MOD'
    p[0] = "MOD\n"
    if(debug): print("P_arit_mod")

def p_arit_1sum(p):
    'arit : 1SUM'
    p[0] = "PUSHI 1 \nADD \n"
    if(debug): print("P_arit_1sum")

def p_arit_1sub(p):
    'arit : 1SUB'
    p[0] = "PUSHI 1 \nSUB \n"
    if(debug): print("P_arit_1sub")

# Explicação: Irá utilizar a função definida no ficheiro de funções vmAbs. Remove o valor inicial e deixa so o resultado.
# Resultado: É inserido o absoluto do valor no topo da stack.
def p_arit_abs(p):
    'arit : ABS' 
    p[0] = "// Função ABS (sistema) \nPUSHA vmAbs \nCALL \nSWAP \nPOP 1 \n// Fim Função ABS (sistema) \n"
    if(debug): print("P_arit_abs")

def p_arit_2div(p):
    'arit : 2DIV'
    p[0] = "PUSHI 2 \nDIV \n"
    if(debug): print("P_arit_2div")
    
# ----------------------------------------------------------------- COMMENT ----------------------------------------------------------------- 
def p_comment_one(p):
    'comment : COMMENT' 
    p[0] = ''
    if(debug): print("P_comment_one")

def p_op_endcomment(p):
    'comment : ENDCOMMENT' 
    p[0] = '' 
    if(debug): print("P_comment_endcomment")

# ----------------------------------------------------------------- CREATEFUNC -----------------------------------------------------------------
# Quando uma função é definida o seu codigo é armazenado para quando for chamada ser inserido diretamente
def p_createfunc(p):
    'createfunc : COLON ID contfunc SEMICOLON'

    p[0] = ''
    global funcs, funcoesProtegidas

    # Lançar erro caso já esteja definida esta função
    if(p[2] in funcs):
        raise Exception(f"Erro de compilacao, funcao \"{p[2]}\" duplicada!")
    
    # Impedir que o utilizador use função com nome de função do sistema
    if(p[2] in funcoesProtegidas): 
        raise Exception(f"Erro de compilacao, nome \"{p[2]}\" utilizado por funcao do sistema! \nFunções utilizadas pelo sistema: {funcoesProtegidas}")

    # Comentarios para identificar as funções
    startComment = '// Função ' + p[2] + '\n'
    endComment   = "// Fim função " + p[2] + "\n"

    # Armazenar o codigo da função
    funcs[p[2]] = startComment + p[3] + endComment # Armazenar o codigo da função
    if(debug): print("P_createfunc, Função guardada")
    
# ----------------------------------------------------------------- CALLFUNC -----------------------------------------------------------------
def p_callfunc(p):
    'callfunc : ID' 
    global funcs

    print(str(funcs))

    # Verificar se a função foi definida antes de ser chamada
    if p[1] in funcs:
        p[0] = funcs[p[1]]
    else:
        # Se não estiver definida, gere uma mensagem de erro
        raise Exception(f"Erro de compilacao, identificador de função desconhecido \"{p[1]}\".")
    
    if(debug): print("P_callfunc")
    
# ----------------------------------------------------------------- STACK ----------------------------------------------------------------- 
# DESATIVADO (Funcionamento incorreto)
#def p_cont_pick(p):
#    'cont : NUM PICK cont'
#    p[0] = "PUSHL " + str(p[1]) + '\n' + str(p[3]) 
#    if(debug): print("P_cont_pick")

def p_stack_num(p):
    'stack : NUM'
    p[0] = "PUSHI " + str(p[1]) + '\n'
    if(debug): print("P_stack_num")

def p_stack_dup(p):
    'stack : DUP'
    p[0] = "DUP 1\n" # Dup 1 na vm é duplicar o primeiro elem
    if(debug): print("P_stack_dup")

def p_stack_letra(p):
    'stack : CHARLETRA'
    p[0] = "PUSHI " + str(ord(p[1])) + '\n' # A letra tem de ser int na stack
    if(debug): print("P_stack_letra")

def p_stack_swap(p):
    'stack : SWAP'
    p[0] = "SWAP\n"
    if(debug): print("P_stack_swap")

def p_stack_drop(p):
    'stack : DROP'
    p[0] = "POP 1\n" # Pop 1 na vm tira o primeiro elem da stack 
    if(debug): print("P_stack_drop")

def p_stack_nip(p):
    'stack : NIP' 
    p[0] = "SWAP\nPOP 1\n"
    if(debug): print("P_stack_nip")

def p_stack_2drop(p):
    'stack : 2DROP' 
    p[0] = "POP 2\n"
    if(debug): print("P_stack_2drop")

# Explicação: Guardar os 3 valores no topo da stack na stack temporaria, inserir denovo trocado 
# Resultado: O 3 item foi para o topo
def p_stack_rot(p):
    'stack : ROT'
    vmCode = "STOREG 2 \nSTOREG 1 \nSTOREG 0 \nPUSHG 2 \nPUSHG 1 \nPUSHG 0 \n"
    p[0] = vmCode
    if(debug): print("P_stack_rot")

# Explicação: Armazenar o valor no topo, duplicar o 2 valor, inserir denovo o topo, trocar
# Resultado: Foi duplicado o 2 valor do topo da stack e inserido no topo  
def p_stack_over(p):
    'stack : OVER'
    vmCode = "STOREG 0 \nDUP 1 \nPUSHG 0 \nSWAP \n"
    p[0] = vmCode
    if(debug): print("P_stack_over")

# Explicação: Duplicar o elemento no topo e armazenar, duplicar o 2 elemento e armazenar, inserir os pares por ordem
# Resultado: O par no topo da stack foi duplicado
def p_stack_2dup(p):
    'stack : 2DUP' 
    vmCode = "DUP 1 \nSTOREG 0 \nSTOREG 1 \nDUP 1 \nSTOREG 2 \nSTOREG 3 \nPUSHG 2 \nPUSHG 0 \nPUSHG 3 \nPUSHG 1 \n"
    p[0] = vmCode
    if(debug): print("P_stack_2dup")

# Explicação: Armazenar os dois pares no topo da stack mas inserir com estes trocados, inserir de volta stack  
# Resultado: O 2 pares no topo da stack foram trocados
def p_stack_2swap(p):
    'stack : 2SWAP' 
    vmCode = "STOREG 1 \nSTOREG 0 \nSTOREG 3 \nSTOREG 2 \nPUSHG 0 \nPUSHG 1 \nPUSHG 2 \nPUSHG 3 \n"
    p[0] = vmCode
    if(debug): print("P_stack_2swap")

# Explicação: Armazenar os dois pares, duplicar os valores do 2 par, inserir tudo devolta na stack  
# Resultado: O 2o par foi copiado e inserido no topo da stack
def p_stack_2over(p):
    'stack : 2OVER' 
    vmCode = "STOREG 1 \nSTOREG 0 \ndup 1 \nSTOREG 3 \nSTOREG 5 \ndup 1 \nSTOREG 2 \nSTOREG 4 \nPUSHG 2 \nPUSHG 3 \nPUSHG 0 \nPUSHG 1 \nPUSHG 4 \nPUSHG 5 \n"
    p[0] = vmCode 
    if(debug): print("P_stack_2over")

def p_stack_tuck(p):
    'stack : TUCK' 
    vmCode = "DUP 1 \nSTOREG 0 \nSTOREG 2 \nSTOREG 1 \nPUSHG 0 \nPUSHG 1 \nPUSHG 2 \n"
    p[0] = vmCode
    if(debug): print("P_stack_tuck")
# ----------------------------------------------------------------- INPUT -----------------------------------------------------------------
def p_input_key(p):
    'input : KEY' 
    p[0] = "READ \nCHRCODE \n"
    if(debug): print("P_input_key")

# ----------------------------------------------------------------- COMPARE -----------------------------------------------------------------
def p_compare_eq(p):
    'compare : EQ' 
    p[0] = "EQUAL \n"
    if(debug): print("P_compare_eq")

def p_compare_neq(p):
    'compare : NEQ' 
    p[0] = "EQUAL \nPUSHI 0 \nEQUAL \n"
    if(debug): print("P_compare_neq")

def p_compare_menor(p):
    'compare : MENOR' 
    p[0] = "INF \n"
    if(debug): print("P_compare_menor")

def p_compare_maior(p):
    'compare : MAIOR' 
    p[0] = "SUP \n"
    if(debug): print("P_compare_maior")

def p_compare_menoreq(p):
    'compare : MENOREQ' 
    p[0] = "INFEQ \n"
    if(debug): print("P_compare_menoreq")

def p_compare_maioreq(p):
    'compare : MAIOREQ' 
    p[0] = "SUPEQ \n"
    if(debug): print("P_compare_maioreq")

def p_compare_zeroeq(p):
    'compare : ZEROEQ' 
    p[0] = "NOT \n"
    if(debug): print("P_compare_zeroeq")

def p_compare_zeromaior(p):
    'compare : ZEROMAIOR' 
    p[0] = "PUSHI 0 \nSUP \n"
    if(debug): print("P_compare_zeromaior")

def p_compare_zeromenor(p):
    'compare : ZEROMENOR' 
    p[0] = "PUSHI 0 \nINF \n"
    if(debug): print("P_compare_zeromenor")

def p_compare_zeroneq(p):
    'compare : ZERONEQ' 
    p[0] = "NOT \nPUSHI 0 \nEQUAL \n"
    if(debug): print("P_compare_zeroneq")

def p_compare_negate(p):
    'compare : NEGATE' 
    p[0] = "PUSHI -1 \nMUL \n"
    if(debug): print("P_compare_negate")

# Explicação: Irá utilizar a função definida no ficheiro de funções vmMin. Remove os 2 valores iniciais e deixa so o resultado.
# Resultado: É inserido o menor valor de entre os 2 no topo da stack.
def p_compare_min(p):
    'compare : MIN' 
    p[0] = "// Função MIN (sistema) \nPUSHA vmMin \nCALL  \nSWAP \nPOP 1 \nSWAP \nPOP 1 \n// Fim Função MIN (sistema) \n" 
    if(debug): print("P_compare_min")

# Explicação: Irá utilizar a função definida no ficheiro de funções vmMax. Remove os 2 valores iniciais e deixa so o resultado.
# Resultado: É inserido o maior valor de entre os 2 no topo da stack.
def p_compare_max(p):
    'compare : MAX' 
    p[0] = "// Função MAX (sistema) \nPUSHA vmMax \nCALL  \nSWAP \nPOP 1 \nSWAP \nPOP 1 \n// Fim Função MAX (sistema) \n"
    if(debug): print("P_compare_max")

# ----------------------------------------------------------------- PRINT -----------------------------------------------------------------
def p_print_strprint(p):
    'print : STRPRINT' 
    p[0] = f"PUSHS \"{p[1]}\" \nWRITES \n"
    if(debug): print("P_print_strprint")

def p_print_strprint2(p):
    'print : STRPRINT2' 
    p[0] = f"PUSHS \"{p[1]}\" \nWRITES \n"
    if(debug): print("P_print_strprint2")

# Nota: O forth adiciona um espaço depois do print de cada numero
def p_print_ponto(p): 
    'print : PONTO'
    p[0] = "WRITEI \nPUSHS \" \" \nWRITES \n"
    if(debug): print("P_print_ponto")

def p_print_space(p):
    'print : SPACE' 
    p[0] = "PUSHS \" \" \nWRITES \n" + str(p[2]) 
    if(debug): print("P_print_space")

def p_print_cr(p):
    'print : CR' 
    p[0] = "WRITELN \n"
    if(debug): print("P_print_cr")

# Função utilizada esta definida no ficheiro funcoes.txt
def p_print_spaces(p):
    'print : SPACES'
    p[0] = f"STOREG 0 \nPUSHA vmSpaceLoop \nCALL\n" 
    if(debug): print("P_print_spaces")

# CUIDADO: Esta implementação do emit não irá transformar o int no caracter correspondente, 
# , já que não é possivel realizar esta conversão na EWVM, 
# , foi ponderada a criação de um função com uma grande quantidade de ifs para realizar a conversão.
def p_print_emit(p):
    'print : EMIT' 
    p[0] = "WRITECHR \n"
    if(debug): print("P_print_emit")

# ----------------------------------------------------------------- CONDS -----------------------------------------------------------------
def p_cond_iet(p):
    'cond : IF cont ELSE cont THEN' 
    
    # Contador para o numero de condicionais
    global condCounter
    id = str(condCounter) 

    # Criação do nome das labels
    labelIf = "if" + id; labelElse = "else" + id; labelThen = "then" + id

    # Criação do codigo
    chamada = f"PUSHI 0 \nJZ {labelIf} \n"                                                                                          
    conteudoIF = f"{labelIf}: \nJZ {labelElse} \n{p[2]}JUMP {labelThen} \n"  
    conteudoELSE = f"{labelElse}: \n{p[4]}JUMP {labelThen}\n" 
    conteudoTHEN = f"{labelThen}: \n"

    # Comentarios
    startComment = f"// Condicional {id}\n"
    endComment   = f"// Fim do condicional {id}\n"

    p[0] = startComment + chamada + '\n' + conteudoIF + '\n' + conteudoELSE + '\n' + conteudoTHEN + '\n' + endComment 

    condCounter += 1
    
    if(debug): print("P_cond_iet")

def p_cond_it(p):
    'cond : IF cont THEN' 
    
    # Contador para o numero de condicionais
    global condCounter
    id = str(condCounter) 

    # Criação do nome das labels
    labelIf = "if" + id; labelThen = "then" + id

    # Criação do codigo
    chamada = f"PUSHI 0 \nJZ {labelIf} \n"                                                                                          
    conteudoIF = f"{labelIf}: \nJZ {labelThen} \n{p[2]} \nJUMP {labelThen} \n"  
    conteudoTHEN = f"{labelThen}: \n"

    # Comentarios
    startComment = f"// Condicional {id}\n"
    endComment   = f"// Fim do condicional {id}\n"

    p[0] = startComment + chamada + '\n' + conteudoIF + '\n' + conteudoTHEN + '\n' + endComment 

    condCounter += 1
    
    if(debug): print("P_cond_it")

# ----------------------------------------------------------------- CICLE -----------------------------------------------------------------
def p_cicle_counter(p):
    'cicle : I'
    p[0] = 'PUSHG 6 \n'
    if(debug): print("P_cicle_counter")


def p_cicle_counted(p):
    'cicle : DO cont LOOP'

    global doCounter
    id = str(doCounter)
    
    chamada = f"PUSHA do{id} \nCALL"
    preparacao = f"""
do{id}: 
ALLOC 2 
PUSHFP  
LOAD -1 // Guardar counter 
STORE 0 
PUSHST {id} 
PUSHFP 
LOAD -2 // Guardar limite 
STORE 1 
PUSHA doLoop{id} 
CALL 
RETURN """
    
    ciclo = f"""
doLoop{id}:
PUSHST {id}
LOAD 0 // Carregar counter
DUP 1 
STOREG 6 // Armazenar valor atual do contador para o I conseguir ler 
PUSHST {id}
LOAD 1 // Carregar limite
INF
JZ endLoop{id}
// Conteudo\n{p[2]}// Fim conteudo
PUSHST {id}
PUSHST {id}
LOAD 0 // Carregar counter
PUSHI 1
ADD  
STORE 0 // Store Counter++
JUMP doLoop{id}"""
    
    fimcicle = f"endLoop{id}: \n"

    p[0] = chamada + '\n' + preparacao + '\n' + ciclo + '\n' + fimcicle

    doCounter += 1
    if(debug): print("P_print_emit")

# ----------------------------------------------------------------- VARIAVEIS -----------------------------------------------------------------
def p_vars_variable(p):
    'vars : VARIABLE ID'
    global vars
    global numVars
    p[0] = ''

    # Proteção de erros
    if(p[2] in vars):
        raise Exception(f"Erro de compilacao, variavel \"{p[2]}\" duplicada!")
    if(p[2] in funcs):
        raise Exception(f"Erro de compilacao, nome utilizado por função \"{p[2]}\"!")
    if(p[2] in funcoesProtegidas):
        raise Exception(f"Erro de compilacao, nome utilizado por função do sistema \"{p[2]}\"!")
    
    # Adicionar a variavel ao conjunto (Será dado o 'pushi 0' antes do start depois)
    vars[p[2]] = {p[2] : numVars}

    numVars += 1  

    if(debug): print("P_vars_variable, Variavel guardada")

def p_vars_fetch(p):
    'vars : ID FETCH'
    global vars
    global numVars

    # Proteção de erros
    if(p[1] not in vars):
        raise Exception(f"Erro de compilacao, variavel nao existe \"{p[2]}\"!")

    valorStack = vars.get(p[1])[p[1]] + memSys # Obter a posição em que a variavel se encontra na VM
    p[0] = f"PUSHG {valorStack} \n"

    if(debug): print("P_vars_fetch")

def p_vars_store(p):
    'vars : ID STORE'
    global vars
    global numVars

    # Proteção de erros
    if(p[1] not in vars):
        raise Exception(f"Erro de compilacao, variavel nao existe \"{p[2]}\"!")

    valorStack = vars.get(p[1])[p[1]] + memSys # Obter a posição em que a variavel se encontra na VM
    p[0] = f"STOREG {valorStack} \n"

    if(debug): print("P_vars_store")

#------------------------------- REGRAS PARA EMPTY -------------------------------
def p_empty(p):
    'empty :'
    pass
    if(debug): print("P_empty")

#------------------------------- ERROS -------------------------------
def p_error(p):
    if p:
        raise Exception(f"AnaSin: Erro gramatical na posição {p.lexpos}: token {p.value}, tipo {p.type}")
    else:
        raise Exception("AnaSin: Erro, fim inesperado do input")

#################################### PARSER ####################################
# Obter argumentos do programa e trata-los
argumentos = sys.argv
tratarArgumentos(argumentos)

# Inicio
if(debug): print("MODO DEBUG ATIVO:")
if(debug): print("Memoria para o sistema: " + str(memSys))
if(debug): print("Pasta de resultados: " + localResultado)
if(debug): print("Ficheiro com funções do sistema: " + ficheiroFuncoes)

# Proteger o utilizador de criar funçoes com o mesmo nome das do sistema
funcoesProtegidas = carregarFuncProtegidas(ficheiroFuncoes)
if(debug): print("Funcoes protegidas: " + str(funcoesProtegidas)) 
    
# Construir o parser
parser = yacc.yacc()

# Iterar o input
result = parser.parse(sys.stdin.read())

# Conteudo no inicio e fim do resultado final
memoriaSistema = "// Memoria do sistema\n" + criarMemoria(memSys) + '\n'
memoriaVariaveis = "// Memoria das variaveis\n" + criarMemoriaVars(vars)
inicio =  memoriaSistema + memoriaVariaveis + "\nstart\n"
fim = "stop\n\n" + carregarTxt(ficheiroFuncoes)

# Construir resultado final
final = inicio + result + fim

# Obter resultado final e trata-lo
print()
print("RESULTADO FINAL:")
print(final)
guardarResultado(localResultado, final)
print("Resultado armazenado com sucesso em: " + localResultado + "/resultado.txt")