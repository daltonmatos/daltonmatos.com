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




