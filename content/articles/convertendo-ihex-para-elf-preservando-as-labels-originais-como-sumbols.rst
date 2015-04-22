:title: Ihex para ELF com simoblos
:author: Dalton Barreto
:date: 2014-04-17
:status: draft


Ideia geral
===========

Quando convertemos um iHex para ELF perdemos todas as labels originais do ASM. Na verdade só de compilar o ASM as labels já são convertidas em endereços absolutos.

Mas olhando o conteúdo do arquivo ``.map`` gerado pelo avrasm2, podemos re-localizar esses símbolos no ELF final. Olhando uma instrução do ELF temos:

.. code-block:: objdump


  00000080 <_binary_build_blink_jmp_asm_bin_start>:
    80:	0c 94 02 00 	jmp	0x4	; 0x4 <__zero_reg__+0x3>
    84:	11 24       	eor	r1, r1

O endereço ``02 00``, que na verdade é ``00002`` vai aparecer no ``.map``. Olhando lá sabemos que quaisquer labels que estavam originalmente no edereço ``0x0002`` estão agora em ``0x4``.

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



.. [#] `Endianness <http://en.wikipedia.org/wiki/Endianness>`_
