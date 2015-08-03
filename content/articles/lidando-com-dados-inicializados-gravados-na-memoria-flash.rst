:title: Flash Memory
:date: 2015-04-26
:status: draft
:author: Dalton Barreto





Algumas ideias para se passar dados da memria flash do C pra asm e do asm pra C.


C => ASM
========

.. code-block:: c

  char *a PROGMEM = "abc";


call_asm_routine(a);

No assembly:

; recebe o parametroem r25:r24 ? Se sim:
mov r26, 25
mov r27, r24
movw z, x ; x é r25:r24

;conferir se o C já passa o valor multiplicado por 2 !! Senão, multiplicar.
shift z, 1

call PrintString

Deve dar para acessar um .db definido no assembly dessa forma:

.. code-block:: c

  extern char *a;


pgm_read_byte(a);

e no assembly:

a:
  .db 10, 20


asm para C
==========

Posicionar *todos* os .db .dw logo após o interrupt vector e marcar esse inicio:

unused:
  reti

data_init:
.include "data.inc"


aí a macro ldz ficaria:

.macro ldz
addiw @0, offset ; offset deve ser par para não mexer no bit 1.
mov zh, high(@0)
mov zl, low(@0)
.endmacro


Pode ser que funcione!!!
========================

Eiste um jeito de deixar todos os .db .dw no assembly. Basta olhar onde o "blob" será posicionado no ELF final (por exempo 0x80) e adicionar 0x40 a qualquer referencia a qualquer label.

Para labels carregadas no Z, pois será usada na instrução lpm precisamos adicionar 2 * 0x40. Pois a instrução espera o endereço "shiftado" de 1 bit pra esquerda.
Para labels que são usadas diretamente (como seleção de fonte, por exemplo), basta somar 0x40 (validar!)

Funciona!!! Mas ainda não descobri como calcular o offset corretamente. Ainda está na tentativa e erro. Compilo o código final, vejo uma instrução "ldz" e confiro se o endereço foi passado corretamente. Ajusto o offset até o endereço ficar correto.


O problema dos .db e .dw
========================

As instrucoes ``.db`` e ``.dw`` reservam espaço para dados incializados. Esses dados ficam "espalhados" pela memória flash, exatamente na posição em que são encontrados no código. Basta olhar o valor que está no arquivo .map para saber onde esse dado estará na memória flash. O problema é que não dá pra "realocar" esses simbolos (da mesma forma que podemos fazer com chamadas call). Isso porque geralmente esse valores são carregados pra um registrador específico e isso gera múltiplas instrucoes, veja:

.. code-block:: asm

  .macro print_addr
    ldz @0
    movw x, z
    call PrintNumberLF
    lrv X1, 0
  .endm

   print_addr hello

   hello:  .db "HELLO", 0

Esse código gera esse assembly:

.. code-block:: objdump

 17a8:       e8 ef           ldi     r30, 0xF8       ; 248
 17aa:       fb e0           ldi     r31, 0x0B       ; 11
 17ac:       df 01           movw    r26, r30
 17ae:       0e 94 49 08     call    0x1092  ; 0x1092 <_binary_main_bin_start+0x1092>

Para o segunte .map:

CSEG hello        00000bf8



O problema é que o endereço do símbolo **já foi resolvido**! E não temos como instruir o avr-gcc para realocar esses valores, mesmo que saibamos colocar esse símbolona tabela de realocação.

A princípio, **todos** os .db .dw são carregados com a macro ``ldz`` que é essa:



Gravação/Leitura de valores da memoria RAM (RamVariables) - OK
==============================================================

Algumas instruçoes gravam/lêm valores da variaveis que o codigo guarda na memoria. Um exemplo, quando escolhemos que fonte usar:


  lrv FontSelector, f6x8

Confirmar, de alguma forma, se o endereço da RamVariable `FontSelector` vai mudar quando juntarmos com C. Talvez não mude pois o avr-gcc precisa configurar o chip da mesma forma, por exemplo, escolhendo inicio e fim da RAM: Não muda! Podemos começar no C, ir pro Assembly e usar RamVariables (save/load) e tudo funciona.



Gravação/Leitura da EEProm - OK
===============================


Gravar e ler da eeprom usa ldz, testar se o offset faz funcionar a leitura/gravação.

RedeeProm/WriteeeProm usam Z.

Parece funcionar!!! Display funcionou mesmo chmando funcoes (LoadLcdContrast/SetDefaultLcdContrast), que usam ReadeeProm e WriteeEprom;


Tentar compilar o código oficial e juntar com C - Validar
=========================================================

No exemplo do hello-world-st7565 quando incluo mais de uma definição de fonte (ou até apenas uma que não seja a f6x8), dá um erro de "out of range error" no momento de adicionar alguns simbolos na symbol table do elf gerado a partir do assembly. Tentar entender isso e resolver.



Usar ldz em todo o codigo - Validar em Voo
=========================

Todas as instrucoes que usam "ldi zl" seguido de "ldi zh" devem ser convertidos para "ldz <param>".

A principio, chamadas como "ldi zl, <N>", não precisam, pois parece que o código está usando o Z apenas como contador e não como preparação para chamar a instrução "lpm".

Fazer teste de voo com essa modificação já feita!

Lembrar de mudar o simbolo TabCh. Todas as fontes devem estar com "+ (offset * 2)". Mas já terei descoberto isso se estiver fazendo o teste de voo, já que a placa não exibit nadano display se isso não estiver correto. =D

Estrategias para conseguir fazer funcionar os .db .dw
=====================================================

 * Talvez se criarmos uma rotina pra **cada** símbolo? Assim poderíamos realocá-la no momento do linking? Como essa rotina saberá "onde foi parar" o símbolo original? Esse é o maior problema.

 * Ter o ssembly chamando uma rotina em C para fazer a carga do endereço do símbolo no registrador z? Assim o assebly não vai "resolver o endereço" em tempo de compilaçao, vai apenas chamar essa rotina (que pode ser realocada). Isso demandaria que todos os simbolos .db .dw fossem migrados para o C. Não dá para migrar aos poucos pois todos os símbolos que permanecerem no assembly terão o problema da mudança de endereço, quando forem linkados ao código C.

 * Mover todos os .db .dw pra o fim do código, olhar onde eles "vão parar" dentro do ELF e mudar a macro para adicionar um "offset" para "corrigir" o endereço do símbolo. Isso pode ser meio que "invalidado" pois todos os símbolos são carregados multiplicados por 2, pois é uma exigência da instruçao ``lpm``.


