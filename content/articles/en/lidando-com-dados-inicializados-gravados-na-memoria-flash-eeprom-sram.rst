:title: Dealing with data stored in the flash, EEPROM and SRAM memories
:date: 2015-09-27
:status: published
:author: Dalton Barreto
:lang: en
:translation: true
:slug: lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram
:url: blog/en/lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram
:save_as: blog/en/lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram/index.html

This post is part of a `series of posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ about mixing legacy assembly (``avrasm2``) and modern C code (``avr-gcc``). If you didn't read the previous posts, it's recomended to do so before proceeding.

Context
=======

So far, in previous posts we have seen just how to make function calls from one language to another, but a very important part of any project with micro-controllers is the ability to write data to the chip memory area (flash memory, for example) . It is quite common to use this memory to store values that will be used by the code. The most common is to see strings being stored for future use, but it is quite possible we keep other values such as constants, numbers and even font definition, in case we are dealing with LCD displays.

In addition to the flash memory, we have two other available memories to use this way. The SRAM memory [#]_ and EEPROM [#]_. We'll see below how to write/read data from these three memories available in the AVR microcontrollers (at least most of them).


Reading/Writing data to SRAM and EEPROM memories
================================================

Both SRAM and EEPROM have fixed positions in every AVR chip, this means that, regardless of the language used, the read/write address will always be the same. This means that we need not to worry about any code relocation when linking with C code. Both ``avr-gcc`` and ``avrasm2`` will correctly initialize the start and end of these two memories and the code can reference these addresses freely.


Reading/Writing data to Flash memory 
====================================

The problem starts when we need to read/write data to flash memory. This happens because the two instructions that we should use (``SPM`` and ``LPM``) work in a peculiar way which I explain below:

When using any of these two statements, we have to use the ``Z`` register to say where we want to read/write our data. So giving a simple example we would have the following code:

.. code-block:: asm
  
  main:
    
    ldi zl, low(data)
    ldi zh, high(data)
    lpm R0, Z

  data:
    .db 02, 03

Looking at this example we might think that at the end of code execution, the value ``02`` will be stored in the ``R0`` register, but unfortunately is not that simple. The problem is that the flash memory is page oriented rather than byte oriented and each page has two bytes. This means that in a ATmega328P, for example, which has 32Kbytes of flash memory, we actually have 16K pages that can be used with the ``LPM/SPM`` instructions. Knowing that every page has two bytes, we must have a way to choose which of these two bytes we want to read/write.

Unlike the general-purpose registers of the AVR, which have 8 bits, the ``Z`` register has 16 bits. In fact, it is the union of two 8-bit general-purpose registers: ``r31`` (``ZH``) and ``r30`` (``ZL``). The way to choose which byte of a page we read/write is using the least significant bit of the ``Z`` register.

When the least significant bit is ``0`` it means that we want to read/write the first byte of the page and when this bit is ``1`` it means we want to read/write the second byte of the page. The remaining bits (1 to 15) serve to indicate the address of the flash memory page that we want to read/write. Knowing this we can now understand why the example above does not work.

In the example above, the page address (which refers to the label ``data:``) is occupying the least significant bit. This happened because we loaded the address of the label ``data:`` directly into the ``Z`` register. Here's an example:

If our label ``data`` were positioned at the address ``0x6e9``, the above example would load the ``Z`` register with the following value:

.. code-block:: text

        ZH        ZL
    00000110  11101001

And what does that mean? According to the datasheet this means that we want to read the second byte of the page (because the least significant bit has a value of ``1``) and we want to read/write that byte in the page with address ``000001101110100``, namely, ``0x374``. That's definitely not what we wanted at the beginning! This sample code is actually reading the page at address ``0x374`` and not the page you want. So how do you read the correct page? What we need to do is load the address of our page beginning at the second least significant bit of the ``Z`` register, thus releasing the first bit to indicate which byte we want to read. There is a very simple way to do this: Just multiply the page address by ``2``, before loading the ``Z`` register. Let's look at the same example as above, but now written properly.

.. code-block:: asm
  
  main:
    
    ldi zl, low(data*2)
    ldi zh, high(data*2)
    lpm r0, Z

  data:
    .db 02, 03

Let's consider our label ``data:`` at the same address: ``0x6e9``. When we run this code, the value that is actually loaded in ``Z`` register is ``0x6e9 * 2``, which is ``0xdd2`` and the ``Z`` register looks like this:

.. code-block:: text

        ZH        ZL
    00001101  11010010


If we do the "decoding" of that value, according to the datasheet, that is, taking the least significant bit to indicate the byte of the page and the rest of the bits to indicate the page address we have the following: The least significant bit has now value ``0``, which means that the first byte of the page will be read/written. And the rest of bits (1-15) have the following value: ``000011011101001`` which is exactly ``0x6e9``! Now the values are correct and the code actually writes the value ``02`` into the ``r0`` register.

And what does all this have to do with our mix of C and Legacy Assembly code? The problem is that these addresses are calculated at **compile** time, that is, before link-editing. This means that when ``avr-gcc`` joins the two codes, all labels will have its addresses changed (as we have seen in previous posts) and it means that **all** flash memory data operations will be incorrect.

In previous posts, to resolve this same kind of problem, that is, the code shift after link-editing we did the parsing of the dissasembly looking for branch instructions (``jmp``, ``rjmp``, etc.) We got the address that these instructions were referencing, we made a reverse search on all labels found in the original code and added an entry in relocation table for each label found. This was done by the two tools I wrote: ``extract-symbols-metadata`` [#]_ and ``elf-add-symbol`` [#]_.

But now we can not do this because a load operation in ``Z`` register ends up as two instructions in the disassembly, like this:

.. code-block:: asm

  ldi r30, 0xE6
  ldi r31, 0x0D

It would be insane to look for this "pattern" throughout the disassembly and try to somehow "edit" the instructions in the final binary. Because of that, this is the only "preparation" you need to do in your assembly code so that you can mix it with a modern C code. In the original code, when you make use of the ``SPM`` or ``LPM`` instructions you need to take into account the displacement that your assembly code will suffer after being linked with the C code. A simple way to do it is, for example, always load values into the ``Z`` register using a macro, like this:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0)
    ldi zh, high(@0)
  .endmacro


After you have already modified the original code to make use of this macro, it is much easier to correct the values that are loaded into the ``Z`` register because we need only to modify this macro, not the entire code. This is an example of using this macro:

.. code-block:: asm

  ldz data*2

What we need now is to find out how much our Assembly code was displaced by the ``avr-gcc`` after it was linked to the C code. We then will add this "offset" to the code of our ``ldz`` macro, so all addresses will be corrected. This only works because our original assembly code consists of a large binary file. If we had multiple assembly files, converted to ``avr-elf32`` and then passed to ``avr-gcc`` for link-editing, we would probably have different offsets for the original code labels. So it's important to keep your Legacy Assembly code as a single binary, converted from Intel Hex to ``avr-elf32`` and passed to the ``avr-gcc`` for linking.

Preparing the ldz macro to consider the offset of the Assembly code 
===================================================================


Since we know that all our labels are displaced after the process of link-editing, we need to prepare our ``ldz`` macro to consider this offset and be able to correct all the addresses loaded into ``Z`` register. Take a simple example:

Let's consider in our example that the label ``data:`` is located at address ``0x6e9``. If we run this Assembly code alone, the call to the ``ldz`` macro would look like the following (we will replace the name of the label by its address for clarity):

.. code-block:: asm

 ldz 0x6e9*2

If we consider an offset of ``0x80`` after a linking with a C code, our call to the macro should look like this:

.. code-block:: asm

 ldz 0x769*2

this happens because ``0x6e9 + 0x80 = 0x769``. It means we can rewrite our macro like this:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0 + offset)
    ldi zh, high(@0 + offset)
  .endmacro

`(Important note: We will understand later why we don't need to add offset * 2, since the @0 value is passed to the macro already multiplied)`.


We can define the constant ``offset`` at the beginning of our assembly code, like this:

.. code-block:: asm

 .equ offset = 0x80


The only way I found to discover the final offest value was to compile the entire code and then look in the disassembly where the legacy code ended up being positioned in the final binary. This is annoying (although it is possible to automate) and error prone but that's what I could do. After discovering the right value, I went back to the Assembly code and added the value of the offset .


A simple way to check if the offset value is correct
====================================================


We can put a simple code at the very beginning of our assembly code to help us check if the chosen ``offset`` is correct.

.. code-block:: asm

  _offset_check:
    ldz _offset_check_data*2
  _offset_check_data:
    .db 01, 02

What this code does is load the address of a label into the ``Z`` register. No one will call this code, but it will be at the very beginning of our Assembly code and it will also appear at the beginning of the final binary disassembly and we can check if the two ``ldi`` statements will be loading the correct value into the ``r31:r30`` (``Z``) registers.

Let's see how this check works. Let's link an assembly code with this check with any C code and let's see how the disassembly looks like.


This will be our C code:

.. code-block:: c

  #include <avr/io.h>


  extern void hello_main();

  int f(){
    return 0;
  }

  void main(){

    f();
    hello_main();

  }


In this code we have the ``hello_main`` routine, that will be implemented in Assembly.

This will be our Assembly code:

.. code-block:: asm

  .org 0x0000

  .equ offset = 0x00

  .macro my_ldz
    ldi zl, low(@0 + (offset))
    ldi zh, high(@0 + (offset))
  .endmacro

  _offset_check:
      my_ldz _offset_data*2

  _offset_data:
    .db 01, 02  

  hello_main:
    call asm_routine_1
    call asm_routine_2
    ...
    ...


Note that the ``offset`` constant still has value ``0x00`` because we do not know where our Assembly code will be positioned in the final binary. Let's see how is the disassebly of a first compile:

.. code-block:: objdump


  build/main_hello.asm.elf:     file format elf32-avr


  Disassembly of section .text:

  00000000 <__vectors>:
     0:	0c 94 34 00 	jmp	0x68	; 0x68 <__ctors_end>
     4:	0c 94 3e 00 	jmp	0x7c	; 0x7c <__bad_interrupt>
     ...
     ...
     ...

  00000080 <f>:
    80:	80 e0       	ldi	r24, 0x00	; 0
    82:	90 e0       	ldi	r25, 0x00	; 0
    84:	08 95       	ret

  0000008a <_offset_check>:
    8a:	e4 e0       	ldi	r30, 0x04	; 4
    8c:	f0 e0       	ldi	r31, 0x00	; 0

  0000008e <_offset_data>:
    8e:	01 02       	muls	r16, r17

  00000090 <hello_main>:
    ...

  00000092 <main>:
    92:	0e 94 40 00 	call	0x80	; 0x80 <f>
    96:	0e 94 48 00 	call	0x90	; 0x90 <hello_main>

What we must note in this disassembly is the point that our assembly code has been placed. We can see that it was positioned after the ``f()`` (written in C) function . Our Assembly code starts at address ``0x008a``. We can also note that the current ``offset`` with value ``0`` is incorrect. Let's see why.

.. code-block:: objdump


  0000008a <_offset_check>:
    8a:	e4 e0       	ldi	r30, 0x04	; 4
    8c:	f0 e0       	ldi	r31, 0x00	; 0

  0000008e <_offset_data>:
    8e:	01 02       	muls	r16, r17

Here we can see that the two ``ldi`` statements, which are responsible for loading the address of the label ``_offset_data`` into the ``Z`` register (``r31:r30``), are incorrect. Our label is located at address ``0x008e``, but what is being loaded into registers ``r31:r30`` is ``0x0004``, which is clearly wrong.

Now let's see how is the disassembly when we add the correct offset, in this case ``0x008a``, which is exactly the point where our Assembly code is positioned in the final binary.

As we didn't add any new C code, we will only look at the part of the disassembly that has really changed.

.. code-block:: objdump

  0000008a <_offset_check>:
    8a:	ee e8       	ldi	r30, 0x8E	; 142
    8c:	f0 e0       	ldi	r31, 0x00	; 0

  0000008e <_offset_data>:
    8e:	01 02       	muls	r16, r17


Now looking at the ``ldi`` instructions we see that it loads the correct address, which is ``0x008e``. This is exactly the address of our label ``_offset_data``. Note that the values are already multiplied by 2, thats because we are looking at a ``avr-elf32`` disassembly, where new addresses are twice the original addresses (foun in the ``.map`` file  produced by ``avrasm2``).

With this offset adjustment, your assembly code can run with the C code and still make free use of flash memory for read/write data.

Bonus
=====

Now that we can call code of the two languages and freely use flash memory to read/write data, would be interesting to be able to declare new constants in C code and pass them to the Assembly code. Thinking about a possible migration from Assembly to C, it is important to migrate gradually, and that includes constant definitions. Below we will see how to do both: Declare in the C code a value that is saved in flash memory and pass it to the Assembly code as a function parameter and declare in the Assembly code a value that is saved in flash memory and pass it to the code C.


Declaring a value in C and passing it to Assembly
=================================================

This is our C code where we declare a variable that will be stored in tha flash memory.

.. code-block:: c

  #include <avr/io.h>

  const char p[] PROGMEM = {"Hello from C."};

  extern void hello_main(const char []);

  void main(){
    hello_main(p);
  }


When we make the call to the ``hello_main()`` Assembly routine, the address of ``p`` is passed in registers ``r25:r24``. let's see the disassembly:

.. code-block:: objdump

  00000dce <main>:
   dce:   8c e7           ldi     r24, 0x7C       ; 124
   dd0:   90 e0           ldi     r25, 0x00       ; 0
   dd2:   0e 94 a2 06     call    0xd44   ; 0xd44 <hello_main>
   ddc:   08 95           ret


We see in this case that the value that is passed is ``0x007c``. The good news is that this value is ready to be used with the ``LPM/SPM`` instructions, that is, is already multiplied by 2. Assembly code needs only to move this value into ``Z`` register and use normally. Let's look at the assembly code that will receive this value:

.. code-block:: asm

  hello_main:
    mov zl, r24
    mov zh, r25
    lpm r0, Z    

Declaring a value in Assembly and passing it to C
=================================================

Now we will do the same, but with the constant defined in the Assembly. Let's look at the C code that will receive the address of the flash memory where the data is stored.

.. code-block:: c

  #include <avr/io.h>
  #include <avr/pgmspace.h>

  const char p[] PROGMEM = {"Hello from C."};

  extern void hello_main(const char []);

  char c_read_flashbyte(char p[]){
    return pgm_read_byte_near(p);
  }

  void main(){
    hello_main(p); 
  }


In this code we call the routine ``hello_main`` which is written in Assembly. This routine calls back the C code using the function ``c_read_flashbyte()``, this time passing as parameter the address where the data is stored. Then we read this data with the ``pgm_read_byte_near()`` and return the value read to the Assembly. Let's look at the assembly code:

.. code-block:: asm
  
  hello_main:

    ldi r25, high(flash_byte_from_asm*2 + offset)
    ldi r24, low(flash_byte_from_asm*2 + offset)
    call c_read_flashbyte
    
  flash_byte_from_asm:  .db "X", 0

Let's see the disassembly of all this:

.. code-block:: objdump

  ...
  ...

  00000d56 <hello_main>:
   dbe:	9d e0       	ldi	r25, 0x0D	; 13
   dc0:	80 ef       	ldi	r24, 0xF0	; 240
   dc2:	0e 94 56 00 	call	0xac	; 0xac <c_read_flashbyte>
   ...
   ...
   ...
   ...

  00000df0 <flash_byte_from_asm>:
   df0:	58 00       	.word	0x0058	; ????

  ...
  ...

  000000ac <c_read_flashbyte>:
    ac:	fc 01       	movw	r30, r24
    ae:	84 91       	lpm	r24, Z
    b0:	08 95       	ret

We pass the address in the registers ``r25:r24``. Note that we are passing the correct address, ``0x0DF0``. The function ``c_read_flashbyte`` moves the contents of ``r25:r24`` into ``Z`` (``r31:r30``) and reads the data with the ``LPM`` instruction, storing the result in ``r24``, which now holds the value: ``X``.

So to pass any address declared in the Assembly to C we must always consider the offset that this code suffered when it was positioned at the final binary.

.. [#] `Static random-access memory <https://en.wikipedia.org/wiki/Static_random-access_memory>`_
.. [#] `EEPROM <https://en.wikipedia.org/wiki/EEPROM>`_
.. [#] `extract-symbols-metadata <{filename}/extra/extract-symbols-metadata-v2.py>`_
.. [#] `elf-add-symbol <{filename}/extra/elf-add-symbol-v2.cpp>`_
