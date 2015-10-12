:title: Converting Intel Hex to ELF32-avr and creating the symbol and relocation tables
:author: Dalton Barreto
:date: 2015-05-03
:status: published
:slug: convertendo-intel-hex-para-elf32-avr-mantendo-tabela-de-simbolos-e-tabela-de-realocacao
:lang: en
:translation: true
:tags: avr, microcontrollers, avr-C, avr-assembly, symbol-table, relocation-table
:url: blog/en/convertendo-intel-hex-para-elf32-avr-mantendo-tabela-de-simbolos-e-tabela-de-realocacao
:save_as: blog/en/convertendo-intel-hex-para-elf32-avr-mantendo-tabela-de-simbolos-e-tabela-de-realocacao/index.html


This post is part of a `series of posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ about mixing C (``avr-gcc``) with Assembly (``AVRASM2``) code. If you didn't read the previous posts yet, it's advisable to do so before proceeding.


Context
=======

In the `previous post <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ we were able to call Assembly code (wrote for ``avrasm2``) from a C code (wrote with ``avr-gcc``). We also realized that there were some limitations in the approach we used and we had to hack the ``.org`` instruction. This means that we would have to change the assembly code every time we added new C code. Today we will use a different approach that makes this hack not necessary anymore.

Looking at our Assembly code
============================

This is the Assembly code we will use to illustrate our post.

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

This code, after compiled and linked with C, generates this disassembly:

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

Let's look closer to understand what is happening. We can see that our assembly code is positioned ate address ``0x0080`` and our ``main`` function calls this address (``call 0x80``).

Looking at the first two line of our assembly routine (``_binary_build_blink_call_asm_bin_start``) we see that the calls are being made to totally wrong asddresses (``0x10`` and ``0xa``). It's easy to realize that the correct addresses would be, respectivelly, ``0x90`` and ``0x8a``. Nothing new here compared to what we have done in the previous post. The good news is that we can show the compiler where are all our assembly routines and we do this using the Symbol Table [#]_.

Manipulation the Symbol Table
=============================

The Symbol Table tells the compiler where are each part of the code, in this case, where are each of the assembly routines. Let's rewind a bit and look at the original Symbol Table of our compiled assembly code, converted from the HEX file. We will see that we have only the symbols created by ``avr-objcopy`` during conversion.

.. code-block:: text

  SYMBOL TABLE:
  00000000 l    d  .text	00000000 .text
  00000000 g       .text	00000000 _binary_build_blink_call_asm_bin_start
  00000016 g       .text	00000000 _binary_build_blink_call_asm_bin_end
  00000016 g       *ABS*	00000000 _binary_build_blink_call_asm_bin_size

And the disassembly:

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

(Note that in this disassembly the address of the two first instructions are correct. That's because this code was not yet linked with C)

When we convert from HEX to ELF we lose all original Assembly symbols (labels). In fact, during the compilation all symbols are resolved to absolute addresses.

It happens that ``avrasm2`` is able to generate, during code compilation, two aditional files: One contains all labels and its final addresses (``.map, -m option``) and the other has the final assembly code, still in text format but with all adresses resolved (``.lst, -l option``). Looking ate the ``.lst`` we see how our ``_blinks`` routine turned out to be.

.. code-block:: text

                    .org 0x0000
                   
                   _blinks:
  000000 940e 0008   call _clear
  000002 940e 0005   call _real_code
  000004 9508        ret
                   
                   _real_code:
  000005 e07a        ldi r23, 0xa
  000006 0f87        add r24, r23
  000007 9508        ret
                   
                   _clear:
  000008 2411        clr r1
  000009 2799        clr r25
  00000a 9508        ret 


The ``call`` intruction was encoded to ``940e 0008``. The first part is the opcode and the second is the address to which this instructin will transfer the control of the code.

In the file that contains all the labels and its addresses, we have the following:

.. code-block:: text

  CSEG _blinks      00000000
  CSEG _clear       00000008
  CSEG _real_code   00000005

Here we have all three symbols: ``_blinks``, ``_clear`` e ``_real_code``. Looking a the ELF disassembly we see that the first ``call`` instruction was encoded as ``0e 94 08 00``, which is essentially the same we had in the ``.lst`` file.

ELF:

.. code-block:: objdump

  00000000 <_blinks>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_binary_build_blink_call_asm_bin_start+0x10>

.lst:

.. code-block:: text

                   _blinks:
  000000 940e 0008   call _clear
                   

The only difference is that they are represented with differend endianness [#]_. In the ELF we have the least significant byte first (left most) and in the ``.lst`` has the least significant byte last (right most). This means that our ``_clear`` routine, which was at address ``0x0008`` in the HEX is now ar adress ``0x10`` in the ELF.

I still don't fully understand why the instruction encoding shows ``0008`` but the disassembly shows ``call 0x10`` (one is two times the other!), but I realized that, at first, the addresses always match! That is, the ELF addresses are always two times the HEX addresses. Maybe this is related with how the ELF represents the instructions internally. The instruction that actually goes to the AVR is indeed ``0e 94 08 00``, that is, the ``call`` will jump to the address ``0008`` in the AVR flash memory, but since we are adding symbols to the ELF file we need to obey its addresses.

Now that we know where in the ELF are our assembly routines (``_clear`` e ``_real_code``) we can add them to the symbol table. As I didn't find any tool that were able to add symbols to an ELF file I wrote my own [#]_ that does this. I called it ``elf-add-symbol``. Our new symbol table is as follows (more about how it was added: `Process Automation`_):

.. code-block:: text

  SYMBOL TABLE:
  00000000 l    d  .text	00000000 .text
  00000000 g       .text	00000000 _blinks
  00000010 g       .text	00000000 _clear
  0000000a g       .text	00000000 _real_code

The symbol table is simple. We have the symbol address, the section to which this symbol belongs to, the size of the symbol and the name of the symbol. The ``g`` and ``l`` flag mean, respectively, "Global Symbol" and "Local Symbol". This is important as only global symbols are available during linking.

After we do this, even the disassembly changes and becomes easier to understand, since we can now see where each routine begins:

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

That helps, but when we link this code with a C code, even after manipulation the symbol table, we still remain with wrong final addresses. Let's see the disassembly after the linking.

.. code-block:: objdump

  00000080 <_blinks>:
    80:   0e 94 08 00     call    0x10    ; 0x10 <__zero_reg__+0xf>
    84:   0e 94 05 00     call    0xa     ; 0xa <__zero_reg__+0x9>
    88:   08 95           ret

  0000008a <_real_code>:
    8a:   7a e0           ldi     r23, 0x0A       ; 10
    8c:   87 0f           add     r24, r23
    8e:   08 95           ret

  00000090 <_clear>:
    90:   11 24           eor     r1, r1
    92:   99 27           eor     r25, r25
    94:   08 95           ret

  00000096 <main>:
    96:   80 e0           ldi     r24, 0x00       ; 0
    98:   0e 94 40 00     call    0x80    ; 0x80 <_blinks>


Our assembly code is again positioned at ``0x0080`` and even with a correct symbol table and out routines at ``0x008a`` and ``0x0090`` both ``call`` instrcutions are still thinking that the routines are, repectively, at ``0x10`` and ``0xa``. 

This happens because the Assembly code is just **copied** into an address inside the final binary during the linking process. We need, somehow, show the compiler that the ``_real_code`` and ``_clear`` routines will change location and because of this the compiler has to adjust any instructions in the code that references them. This is the job of the Relocation Table.

Relocation Table
================

The Relocation Table [#]_ exists exactly to tell the compiler which symbols will change address and which instructions will nedd to have its target addresses adjusted. To undestand this table we need to look back to the original disassembly (before linking with C code).

.. code-block:: objdump

  Disassembly of section .text:

  00000000 <_blinks>:
     0:   0e 94 08 00     call    0x10    ; 0x10 <_clear>
     4:   0e 94 05 00     call    0xa     ; 0xa <_real_code>
     8:   08 95           ret

  0000000a <_real_code>:
     a:   7a e0           ldi     r23, 0x0A       ; 10
     c:   87 0f           add     r24, r23
     e:   08 95           ret

  00000010 <_clear>:
    10:   11 24           eor     r1, r1
    12:   99 27           eor     r25, r25
    14:   08 95           ret

(Using the same tool [3]_ I wrote to manipulate the symbol table we can create the relocation table)

Let's see the Relocation Table in detail (more on how it was created: `Process Automation`_):

.. code-block:: text

  RELOCATION RECORDS FOR [.text]:
  OFFSET   TYPE              VALUE 
  00000000 R_AVR_CALL        _clear
  00000004 R_AVR_CALL        _real_code

Explaining the table: Each ELF section can have its own relocation table. In this case this table belongs to the ``.text`` section, that is, it references only symbols that are in the ``.text`` section. This is where our code is. The ``OFFSET`` field stores the address of the instruction that will be edited (more on this later). The ``TYPE`` stores the type of the relocation [#]_,  I confess that I extracted the value of the ``R_AVR_CALL`` relocatin type from and ELF file generated by ``avr-gcc`` (more about this: `Reverse engeneering the R_AVR_CALL value`_). The field ``VALUE`` stores which symboll is being relocated.

Let's see each entry of the relocation table:

.. code-block:: text

  00000000 R_AVR_CALL        _clear

This entry tells us that the instruction located at address ``0x0000`` (``call 0x10``) is referecing a routine named ``_clear`` and that this routine will be somewhere inside the final binary. Whatever this address will be, this ``call`` instruction will be edited and the value ``0x10`` will be changed to the real address of the ``_clear`` routine.

The same happens to the other entry:

.. code-block:: text

  00000004 R_AVR_CALL        _real_code

Here we have the exact same behavior but the edited instruction will be ``call 0xa`` and the ``0xa`` address will be changed to the final address of the ``_real_code`` routine.

Now that we have an ELF with both the symbol table and the relocation table we can link again to the C code. And we have the following disassembly:

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

The final code is correctly adjusted to point to the right addresses of the assembly routines!

Important to note is that the instruction was indeed changed. Looking at the first ``call`` instruction it is encoded as ``0e 94 48 00`` (before it was ``0e 94 08 00``, remember?) and since the ELF addresses are always two times the HEX addresses we can check that ``0x90`` (``_clear`` routine address in the ELF) is exactly two times ``0x48``, which is the address that is encoded in our new instruction!

This code works when flashed into a AVR!

Process Automation 
==================

What we did here was just a manual analisys of how to reconstruct the symbol and relocation tables so we could relocate all routines that were inside our legacy Assembly code, but in a real world situation with a large Assembly project it is much better to automate this process. To acomplish this I wrote some scripts to do help me do the build automatically.

First I wrote a Python script [#]_ that works as follows:

Given the content of the map file (``.map`` produced by ``avrasm2``) and the ELF disassembly output the script finds out the new address of all symbols and all instrcutions that should be adjusted because of relocated symbol reference. Using this script with the Assembly code of this post, we have this:

.. code-block:: shell-session

  > avr-objdump -d blink_call.asm.elf | python2 extract-symbols-metadata.py blink_call.asm.map
  _blinks 0x0000
  _clear 0x10 0x0
  _real_code 0xa 0x4

If you look closely to this output it represents **exactly** the relocation table. This is the structure of this output:

.. code-block:: text

 <symbol_name> <symbol_address> <address_of_all_instructions_that_references_this_symbol>

Now what we have to do is transform this output into a real relocation table in the ELF file. For this we use the tool ``elf-add-symbol`` [3]_. Assuming we saved this output to ``blink_call.asm.symtab`` we can to the following:

.. code-block:: shell-session

  cat blink_call.asm.symtab | ./elf-add-symbol blink_call.asm.elf

This command modifies the ``blink_call.asm.elf`` file adding the symbol and the relocation tables! After this we are ready to link our ELF with the C code.

Reverse engeneering the R_AVR_CALL value
========================================

The relocation table has a `known strcture <http://wiki.osdev.org/ELF_Tutorial#Relocation_Sections>`_. One of the field is ``r_info``. This field stores two informations: Which symbol is being relocated (8 most significant bits) and which type of relocation will be used (8 least significant bits). When I wrote ``elf-add-symbol``, the library I used (ELFIO [#]_) only had constans for the x86 relocation types, somehow I needed to know what was the value of the right relocation type I needed.

What I did was to compile an Assembly code using ``avr-gcc`` and using the ``avr-readelf`` tool I looked into the generated relocation table:

.. code-block:: readelf

  Relocation section '.rela.text' at offset 0x100 contains 2 entries:
   Offset     Info    Type            Sym.Value  Sym. Name + Addend
  00000000  00000112 R_AVR_CALL        00000000   .text + a
  00000004  00000112 R_AVR_CALL        00000000   .text + c

The I took the ``0x112`` value (``Info`` field) and used the ``ELF32_R_TYPE()`` macro (from the ELFIO [7]_ library). The return value was ``0x12`` which is ``18`` in decimal. Thats why we have the ``#define R_AVR_CALL 18`` in the ``eld-add-symbol`` source-code.

Next post: `Calling modern C code (avr-gcc) from legacy Assembly (avrasm2) <{filename}chamando-codigo-novo-em-c-avr-gcc-a-partir-de-um-codigo-assembly-legado-avrasm2.rst>`_.

.. [#] `ELF Symbol Table <http://wiki.osdev.org/ELF_Tutorial#The_Symbol_Table>`_
.. [#] `Endianness <http://en.wikipedia.org/wiki/Endianness>`_
.. [#] `Código-fonte da ferramenta elf-add-symbol <https://github.com/daltonmatos/avrgcc-mixed-with-avrasm2/blob/master/experiments/tools/elf-add-symbol.cpp>`_
.. [#] `ELF Relocation Table <http://wiki.osdev.org/ELF_Tutorial#Relocation_Sections>`_
.. [#] `AVR ELF Relocation Types <https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=blob;f=include/elf/avr.h;h=115296da404d034d0626ebe57ac2631a6849d239;hb=HEAD#l53>`_
.. [#] `extract-symbols-metadata <https://github.com/daltonmatos/avrgcc-mixed-with-avrasm2/blob/master/experiments/tools/extract-symbols-metadata.py>`_
.. [#] `ElfIO - C++ library for reading and generating ELF files <http://elfio.sourceforge.net/>`_

