:title: Calling C from AVR_ASsembly (AVRASM2)
:author: Dalton Barreto
:date: 2015-04-22
:status: draft


O código ASM (que foi convertido a partir de um .HEX) deve ter seus simbolos adicionados (ver post sobre symbol tables/relocation tables). O símbolos devem estar também na relocation table. A diferença é que o símbolo em questão não pertence a nenhuma section, ou seja, fica como *UND*. Confirmar como adicionar um simbolo com essas características.

Nesse caso específico, como o simbolojá estará inserido na symbol table (por causa da conversão .HEX => ELF) esse símbolo terá que ser editado, ou apagado e re-inserido.

SYMBOL TABLE:
00000000 l    df *ABS*	00000000 main.c
00000000 l    d  .text	00000000 .text
00000000 l    d  .data	00000000 .data
00000000 l    d  .bss	00000000 .bss
0000003e l       *ABS*	00000000 __SP_H__
0000003d l       *ABS*	00000000 __SP_L__
0000003f l       *ABS*	00000000 __SREG__
00000000 l       *ABS*	00000000 __tmp_reg__
00000001 l       *ABS*	00000000 __zero_reg__
00000000 l    d  .text.startup	00000000 .text.startup
00000000 l    d  .comment	00000000 .comment
00000000 g     F .text.startup	00000050 main
00000000         *UND*	00000000 _blinks

relocation table:

RELOCATION RECORDS FOR [.text.startup]:
OFFSET   TYPE              VALUE 
00000002 R_AVR_CALL        _blinks
0000000e R_AVR_7_PCREL     .text.startup+0x0000003c
0000001e R_AVR_7_PCREL     .text.startup+0x00000018
00000020 R_AVR_13_PCREL    .text.startup+0x00000022
00000032 R_AVR_7_PCREL     .text.startup+0x0000002c
00000034 R_AVR_13_PCREL    .text.startup+0x00000036
0000003a R_AVR_13_PCREL    .text.startup+0x0000000c
00000048 R_AVR_7_PCREL     .text.startup+0x00000042
0000004a R_AVR_13_PCREL    .text.startup+0x0000004c
0000004e R_AVR_13_PCREL    .text.startup+0x0000000a

Disassembly:

.. code-block:: objdump

  00000000 <main>:
     0:   80 e0           ldi     r24, 0x00       ; 0
     2:   0e 94 00 00     call    0       ; 0x0 <main>
     6:   25 9a           sbi     0x04, 5 ; 4
     8:   2d 9a           sbi     0x05, 5 ; 5
     a:   90 e0           ldi     r25, 0x00       ; 0
     c:   98 17           cp      r25, r24
     e:   01 f0           breq    .+0             ; 0x10 <main+0x10>
    10:   2d 9a           sbi     0x05, 5 ; 5
    12:   2f ef           ldi     r18, 0xFF       ; 255
    14:   33 ec           ldi     r19, 0xC3       ; 195
    16:   49 e0           ldi     r20, 0x09       ; 9
    18:   21 50           subi    r18, 0x01       ; 1
    1a:   30 40           sbci    r19, 0x00       ; 0
    1c:   40 40           sbci    r20, 0x00       ; 0
    1e:   01 f4           brne    .+0             ; 0x20 <main+0x20>
    20:   00 c0           rjmp    .+0             ; 0x22 <main+0x22>


Pela relocation table, instrução em 0x0002 deve ter seu endereço recalculado para onde estiver o símbolo _blinks.


Ver se faz diferença: A relocation table possui muitas outras entradas, quando fazemos o disassembly junto com o dump da relocation table (avr-objdump -dr ) o disassembly mostra os outros símbolos que seriam realocados, mas a maioria é rjmp. O.o!

.. code-block:: objdump

  00000000 <main>:
     0:   80 e0           ldi     r24, 0x00       ; 0
     2:   0e 94 00 00     call    0       ; 0x0 <main>
                          2: R_AVR_CALL   _blinks
     6:   25 9a           sbi     0x04, 5 ; 4
     8:   2d 9a           sbi     0x05, 5 ; 5
     a:   90 e0           ldi     r25, 0x00       ; 0
     c:   98 17           cp      r25, r24
     e:   01 f0           breq    .+0             ; 0x10 <main+0x10>
                          e: R_AVR_7_PCREL        .text.startup+0x3c
    10:   2d 9a           sbi     0x05, 5 ; 5
    12:   2f ef           ldi     r18, 0xFF       ; 255
    14:   33 ec           ldi     r19, 0xC3       ; 195
    16:   49 e0           ldi     r20, 0x09       ; 9
    18:   21 50           subi    r18, 0x01       ; 1
    1a:   30 40           sbci    r19, 0x00       ; 0
    1c:   40 40           sbci    r20, 0x00       ; 0
    1e:   01 f4           brne    .+0             ; 0x20 <main+0x20>
                          1e: R_AVR_7_PCREL       .text.startup+0x18
    20:   00 c0           rjmp    .+0             ; 0x22 <main+0x22>
                          20: R_AVR_13_PCREL      .text.startup+0x22


Saber se isso, em um ELF gerado a partir de um .HEX isso seria necessário.

