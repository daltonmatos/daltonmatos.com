:title: Ihex para ELF com simoblos
:author: Dalton Barreto
:date: 2014-04-17
:status: draft
:slug: convertendo-intel-hex-para-elf32-avr-mantendo-tabela-de-simbolos-e-tabela-de-realocacao


Esse post faz parte de uma `série de posts <|filename|chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ sobre mistura de código C (avr-gcc) com código Assembly (AVRASM2). Se você ainda não leu os posts anteriores, recomendo que leia antes de prosseguir.

Contexto
========

No `post anterior <|filename|chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ vimos que é possível chamar código assembly (feito com AVRASM2) a partir de codigo C (avr-gcc). Vimos também que existem algumas limitaçoes na estratégia usada, tivemos que ajustar a instrução ``.org`` no código e isos significa que temos que ajustar o código assembly toda vez que adicionarmos mais código C. Nesse post vamos ver uma outra abordagem em que isso não é mais necessário.

Olhando para o exemplo inicial
==============================


Esse será o código assembly que usaremos para ilustrar esse post.

.. code-block:: asm

  .org 0x0000


  _blinks:
    call _clear
    call _real_code
    ret

  _real_code:
    ldi r23, 0xa
    add r24, r23
    ret

  _clear:
    clr r1
    clr r25
    ret 

Esse código, depois de compilado e linkado com um código C produz esse disassembly:

.. code-block:: objdump


  00000080 <_binary_build_blink_call_asm_bin_start>:
    80:   0e 94 08 00     call    0x10    ; 0x10 <__zero_reg__+0xf>
    84:   0e 94 05 00     call    0xa     ; 0xa <__zero_reg__+0x9>
    88:   08 95           ret
    8a:   7a e0           ldi     r23, 0x0A       ; 10
    8c:   87 0f           add     r24, r23
    8e:   08 95           ret
    90:   11 24           eor     r1, r1
    92:   99 27           eor     r25, r25
    94:   08 95           ret

  00000096 <main>:
    96:   80 e0           ldi     r24, 0x00       ; 0
    98:   0e 94 40 00     call    0x80    ; 0x80 <_binary_build_blink_call_asm_bin_start>

Vamos analisar esse código mais de perto e ver o que está acontecendo: Vemos que nosso código assembly foi posicionado no endereço ``0x0080`` e que nossa funcção ``main()`` faz uma chamada a esse endereço (``call 0x80``). Até aí, tudo OK! Agora vamos ver como nossa rotina assembly ficou no final.

Olhando as duas primeiras instruçoes de nossa rotina, vemos que as duas chamadas estão indo para endereços completamente errados (``0x10`` e ``0xa``). É fácil perceber que os endereços corretos deveriam ser, respectivamente, ``0x90`` e ``0x8a``. Até aqui nenhuma novidade em relação ao que já fizemos. Acontece que podemos mostrar ao compilador onde estão nossas rotinas e fazemos isso atráves da tabela de símbolos [#]_.


Manipulando a tabela de símbolos
================================


A tabela de símbolos diz ao compilador onde está cada parte do nosso código, no nosso caso, onde estão cada uma das rotinas assembly. Vamos voltar um pouco e olhar nosso código assembly compilado, mas antes de ser linkado ao código C. Se olharmos a tabela de símbolos veremos que so temos os símbolos criados pelo ``avr-objcopy`` quando convertemos de HEX para ELF.

.. code-block:: text

  SYMBOL TABLE:
  00000000 l    d  .text	00000000 .text
  00000000 g       .text	00000000 _binary_build_blink_call_asm_bin_start
  00000016 g       .text	00000000 _binary_build_blink_call_asm_bin_end
  00000016 g       *ABS*	00000000 _binary_build_blink_call_asm_bin_size

E o disassembly:

.. code-block:: objdump

  00000000 <_binary_build_blink_call_asm_bin_start>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_binary_build_blink_call_asm_bin_start+0x10>
     4:	0e 94 05 00 	call	0xa	; 0xa <_binary_build_blink_call_asm_bin_start+0xa>
     8:	08 95       	ret
     a:	7a e0       	ldi	r23, 0x0A	; 10
     c:	87 0f       	add	r24, r23
     e:	08 95       	ret
    10:	11 24       	eor	r1, r1
    12:	99 27       	eor	r25, r25
    14:	08 95       	ret

(Lembrando que nesse disasembly das duas primeiras instruçoes estão corretas pois o código ainda não foi linkado com o código C)

Como sabemos onde estão nossas duas rotinas (``_clear`` e ``_real_code``) podemos adicionar dois símoblos à tabela de símbolos. Como não encontrei nenhuma ferramenta que adicionasse símbolos a um ELF, escrevei meu pŕoprio código [#]_ que faz isso, chamei a ferramenta de ``elf-add-symbol``. Nossa nova tabela de símbolos ficou assim:

.. code-block:: text

  SYMBOL TABLE:
  00000000 l    d  .text	00000000 .text
  00000000 g       .text	00000000 _blinks
  00000010 g       .text	00000000 _clear
  0000000a g       .text	00000000 _real_code

Depois que fazemos isso, até o disassembly muda e fica mais simples de entender, pois conseguimos ver onde começa cada rotina, veja:

.. code-block:: objdump

  Disassembly of section .text:

  00000000 <_blinks>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_clear>
     4:	0e 94 05 00 	call	0xa	; 0xa <_real_code>
     8:	08 95       	ret

  0000000a <_real_code>:
     a:	7a e0       	ldi	r23, 0x0A	; 10
     c:	87 0f       	add	r24, r23
     e:	08 95       	ret

  00000010 <_clear>:
    10:	11 24       	eor	r1, r1
    12:	99 27       	eor	r25, r25
    14:	08 95       	ret

Isso já ajuda mas ainda sim quando linkamos esse código com o código em C, ficamos com alguns endereços errados. Isso porque esse código assembly é apenas **copiado** para alguma posição dentro do binário final, após a link-edição. Precisamos, de alguma forma, dizer ao compilador que o endereço das rotinas ``_real_code`` e ``_clear`` irá mudar e por isso ele deve ajustar o endereço de chamada de quaisquer instruçoes que fizerem referências a essas rotinas.

Tabela de realocação
====================

A Tabela de realocação [#]_ existe exatamente para dizer ao compilador quais símbolos mudarão de lugar e quais instruçoes ele deve editar e trocar o endereço final. usando a mesma ferramenta que usamos antes, vamos mexer na tabela de realocação.


.. code-block:: text

  RELOCATION RECORDS FOR [.text]:
  OFFSET   TYPE              VALUE 
  00000000 R_AVR_CALL        _clear
  00000004 R_AVR_CALL        _real_code

A tabela funciona da segunte forma. Cada seção do ELF pode ter sua tabela de realocação. Nesse caso, essa tabela de realocação "pertence" à secão ``.text``, ou seja, ela faz referencia apenas a símbolos que existem na seção ``.text``. O campo ``OFFSET`` indica o endereço da instrução que deverá ser editada (veremos isso em detalhe mais adiante). O campo ``TYPE`` indica o tipo de realocação [#]_, confesso que olhei esse valor em um elf gerado pelo avr-gcc (mais sobre isso no fim do post). O campo ``VALUE`` indica qual o símbolo será realocado.

Para entendermais claramente, vamos olhar o disassembly novamente:

.. code-block:: objdump

  Disassembly of section .text:

  00000000 <_blinks>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_clear>
     4:	0e 94 05 00 	call	0xa	; 0xa <_real_code>
     8:	08 95       	ret

  0000000a <_real_code>:
     a:	7a e0       	ldi	r23, 0x0A	; 10
     c:	87 0f       	add	r24, r23
     e:	08 95       	ret

  00000010 <_clear>:
    10:	11 24       	eor	r1, r1
    12:	99 27       	eor	r25, r25
    14:	08 95       	ret


+ Explicar aqui, mostrando no disassembly, cada uma das linhas da relocatin table.






Quando convertemos um HEX para ELF perdemos todas as labels originais do ASM. Na verdade só de compilar o ASM as labels já são convertidas em endereços absolutos.

Mas olhando o conteúdo do arquivo ``.map`` gerado pelo avrasm2, podemos re-localizar esses símbolos no ELF final. Olhando uma instrução do ELF temos:

.. code-block:: objdump


  00000080 <_binary_build_blink_jmp_asm_bin_start>:
    80:	0c 94 02 00 	jmp	0x4	; 0x4 <__zero_reg__+0x3>
    84:	11 24       	eor	r1, r1

O endereço ``02 00``, que na verdade é ``0002`` vai aparecer no ``.map``. Olhando lá sabemos que quaisquer labels que estavam originalmente no edereço ``0x0002`` estão agora em ``0x4``.

Bônus para manipulação da tabela de realocação.


Acontece que o avrasm2 pode gerar, no momento da compilação, dois arquivos adicionais: Um tem todos os labels e seus endereços finais (``.map``) e o outro tem o código assembly final, ainda em formato de texto mas já com todos os endereços resolvidos (``.lst``). Olhando o ``.lst`` vemos como ficou nossa rotina ``_blinks``:

.. code-block:: text

  .org 0x0000
                   
                   _blinks:
  000000 940c 0002   jmp _add
                   
                   _add:
  000002 2411        clr r1
  000003 2799        clr r25
  000004 e07a        ldi r23, 0xa
  000005 0f87        add r24, r23
  000006 9508        ret 

Podemos perceber que a linha do ``jmp`` é codificada como ``940c 0002``. A primeira parte é o código da instrução e a segunda é o endereço para onde ela transfere o controle do código.

No aquivo que contém todos as labels e seus respectivos endereços finais, temos o seguinte:


.. code-block:: text

  CSEG _blinks      00000000
  CSEG _add         00000002

Aqui temos nossos dois símbolos: ``_blinks`` e ``_add``. Olhando o disassembly do arquivo elf vemos que a instrução ``jmp`` foi codificada como: ``0c 94 02 00``, que é essencialmente a mesma coisa que tínhamos no nosso arquivo ``.lst``!

ELF:

.. code-block:: objdump

  00000080 <_binary_build_blink_jmp_asm_bin_start>:
    80:	0c 94 02 00 	jmp	0x4	; 0x4 <__zero_reg__+0x3>

.lst:

.. code-block:: text

                   _blinks:
  000000 940c 0002   jmp _add
                   

A única diferença entre eles parece ser a representação do bit mais significativo [#]_. No ELF a representação está com o byte menos significativo primeiro e no .lst está com byte menos signifcativo por último.

Ainda não entendo porque o código da instrução menciona o endereço ``0002`` e o disassemble mostra ``jmp 0x4``, mas percebi que a primípio os endereços sempre coincidem! =D


Criando a tabela de realocação
==============================


Se temos uma chamada a uma função, precisamos (muitas vezes) ajustar o endereço final da chamada. Exemplo de assembly com chamadas (e sub-chamadas):

.. code-block:: objdump


  Disassembly of section .text:

  00000000 <_blinks>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_clear>
     4:	0e 94 05 00 	call	0xa	; 0xa <_real_code>
     8:	08 95       	ret

  0000000a <_real_code>:
     a:	7a e0       	ldi	r23, 0x0A	; 10
     c:	87 0f       	add	r24, r23
     e:	08 95       	ret

  00000010 <_clear>:
    10:	11 24       	eor	r1, r1
    12:	99 27       	eor	r25, r25
    14:	08 95       	ret


Reparem que as duas primeiras linhas do código são chamadas call a duas rotinas diferentes. O problema é que quando usamos esse código para ser linkado com um código C que, por exemplo, chama a rotina ``_blinks``, as duas chamadas ficam erradas no arquivo final! Pois coninuam sendo feitas pra ``0x10`` e ``0xa``, mesmo as duas rotinas ``_real_code`` e ``_clear`` tendo sido colocadas em outros endereços. Exemplo:

.. code-block:: objdump

 asm de um main.c linkado errado.



O que precisamos fazer é adicionar ao ELF uma tabela de relocação e indicar quals são as chamadas que precisam ter seus endereços realocados. Segue a tabela de realocação:

.. code-block:: objdump

  with_symbols_blink_call.asm.elf:     file format elf32-avr

  RELOCATION RECORDS FOR [.text]:
  OFFSET   TYPE              VALUE 
  00000004 R_AVR_CALL        _real_code
  00000000 R_AVR_CALL        _clear


O ``OFFSET`` indica o endereço da instrução que deve o endereço do call ajustado. E o ``VALUE`` é "para onde" o call deve ir. Como os symbolos ``_real_code`` e ``_clear`` serão colocados em algum endereço no binário final, o linker saberá para qual valor ajustar os calls. Ex:

.. code-block:: objdump

  00000080 <_blinks>:
    80:   0e 94 48 00     call    0x90    ; 0x90 <_clear>
    84:   0e 94 45 00     call    0x8a    ; 0x8a <_real_code>
    88:   08 95           ret

  0000008a <_real_code>:
    8a:   7a e0           ldi     r23, 0x0A       ; 10
    8c:   87 0f           add     r24, r23
    8e:   08 95           ret

  00000090 <_clear>:
    90:   11 24           eor     r1, r1
    92:   99 27           eor     r25, r25
    94:   08 95           ret

Rotina ``_blinks`` com o endereços dos calls corretamente ajustados!


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



Estrategias para conseguir fazer funcionar os .db .dw
=====================================================

 * Talvez se criarmos uma rotina pra **cada** símbolo? Assim poderíamos realocá-la no momento do linking? Como essa rotina saberá "onde foi parar" o símbolo original? Esse é o maior problema.

 * Ter o ssembly chamando uma rotina em C para fazer a carga do endereço do símbolo no registrador z? Assim o assebly não vai "resolver o endereço" em tempo de compilaçao, vai apenas chamar essa rotina (que pode ser realocada). Isso demandaria que todos os simbolos .db .dw fossem migrados para o C. Não dá para migrar aos poucos pois todos os símbolos que permanecerem no assembly terão o problema da mudança de endereço, quando forem linkados ao código C.

 * Mover todos os .db .dw pra o fim do código, olhar onde eles "vão parar" dentro do ELF e mudar a macro para adicionar um "offset" para "corrigir" o endereço do símbolo. Isso pode ser meio que "invalidado" pois todos os símbolos são carregados multiplicados por 2, pois é uma exigência da instruçao ``lpm``.








.. [#] `ELF Symbol Table <http://en.wikipedia.org/wiki/Endianness>`_
.. [#] `Endianness <http://en.wikipedia.org/wiki/Endianness>`_
.. [#] `elf-add-symbol <|filename|elf-add-symbol.cpp>`_
