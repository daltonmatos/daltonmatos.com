:title: Chamando código novo C (avr-gcc) a partir de código legado Assembly (avrasm2)
:author: Dalton Barreto
:date: 2015-07-26
:status: published
:lang: pt
:slug: chamando-codigo-novo-em-c-avr-gcc-a-partir-de-um-codigo-assembly-legado-avrasm2

Esse post faz parte de uma `série de posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ sobre mistura de código C (avr-gcc) com código Assembly (``avrasm2``). Se você ainda não leu os posts anteriores, recomendo que leia antes de prosseguir.

Contexto
========

Uma parte muito importante quando estamos trabalhando com projetos de código misto, nesse caso C e Assembly, é poder chamar livremente códigos das duas linguagens. Temos que poder chamar uma rotina Assemlty a partir do C e temos também que poder chamar código C a partir do Assembly. Até agora, nos posts anteriores, vimos apenas a primeira opção. Nesse post vamos ver como chamar código C a partir de código Assembly.

Entendendo um símbolo externo
=============================

Toda rotina que o código precisa chamar se transforma em um símbolo, que será usado pelo link-editor no momento de gerar o binário final. Vimos isso `no post sobre tabela de símbolos <{filename}convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.rst>`_, onde o próprio avr-gcc cuidava disso pra nós, já que estávamos lidando com um símbolo externo ao código C. Dessa vez teremos um símbolo externo ao código Assembly e por isso precisaremos novamente adicionar esse símbolo de forma manual na tabela de símbolos.

A forma como declaramos, no C, um símbolo externo é essa:

.. code-block:: c

  extern void asm_main();


Olhando a tabela de símbolos criada pelo ``avr-gcc`` temos o seguinte:

.. code-block:: objdump

  Section Headers:
  [  Nr ] Type              Addr     Size     ES Flg Lk Inf Al Name
  [    0] NULL              00000000 00000000 00     00 000 00                   
  [    1] PROGBITS          00000000 00000000 00 AX  00 000 01 .text             
  [    2] PROGBITS          00000000 00000000 00 WA  00 000 01 .data             
  [    3] NOBITS            00000000 00000000 00 WA  00 000 01 .bss              
  [    4] PROGBITS          00000000 0000003e 00 AX  00 000 01 .text.startup     
  [    5] RELA              00000000 00000078 0c     08 004 04 .rela.text.startup 
  [    6] PROGBITS          00000000 00000028 01     00 000 01 .comment          
  [    7] STRTAB            00000000 00000048 00     00 000 01 .shstrtab         
  [    8] SYMTAB            00000000 000000e0 10     09 00c 04 .symtab           
  [    9] STRTAB            00000000 0000004a 00     00 000 01 .strtab           
  Key to Flags: W (write), A (alloc), X (execute)


  Symbol table (.symtab)
  [  Nr ] Value    Size     Type    Bind      Sect Name
  [    0] 00000000 00000000 NOTYPE  LOCAL        0   
  [    1] 00000000 00000000 FILE    LOCAL    65521 main.c 
  [    2] 00000000 00000000 SECTION LOCAL        1   
  [    3] 00000000 00000000 SECTION LOCAL        2   
  [    4] 00000000 00000000 SECTION LOCAL        3   
  [    5] 0000003e 00000000 NOTYPE  LOCAL    65521 __SP_H__ 
  [    6] 0000003d 00000000 NOTYPE  LOCAL    65521 __SP_L__ 
  [    7] 0000003f 00000000 NOTYPE  LOCAL    65521 __SREG__ 
  [    8] 00000000 00000000 NOTYPE  LOCAL    65521 __tmp_reg__ 
  [    9] 00000001 00000000 NOTYPE  LOCAL    65521 __zero_reg__ 
  [   10] 00000000 00000000 SECTION LOCAL        4   
  [   11] 00000000 00000000 SECTION LOCAL        6   
  [   12] 00000000 0000003e FUNC    GLOBAL       4 main 
  [   13] 00000000 00000000 NOTYPE  GLOBAL       0 asm_main 

Esse output foi gerado com a ferramenta ELFIO [#]_, que já vem com um exemplo de implementação chamado ``elfdump``.

Olhando a tabela, vemos que o símbolo ``asm_main`` pertence a um tipo de seção especial ``NULL``. Sabemos isso olhando a coluna ``Sect``, que nesse caso tem o valor ``0``. E na primeira tabela, ``Section Headers:``, a section de índice ``0`` é a ``NULL``. O que precisamos fazer é adicionar nossos símbolos externos também pertencendo a essa seção e esperar que o avr-gcc consiga fazer a link-edição quando estiver gerando o binário final.

Lidando com a impossibilidade de declarar símbolos no Intel Hex
===============================================================

Essa instrução ``extern``, que usamos no ``avr-gcc``, simplesmente não existe quando estamos escrevendo código Assembly com o ``avrasm2``. Isso contece porque o ``avrasm2`` gera apenas um Intel Hex no final de tudo e não existe uma fase de link-edição durante o processo de compilação. Tudo se torna ainda mais complicado pois o código Assembly é compilado de forma totalmente separada do código C e ele "não sabe" que um (ou mais) de seus símbolos, na verdade, tem sua implementação no código C.

Vejamos um exemplo de código assembly onde teremos um símbolo externo.

.. code-block:: asm

  .org 0x0000

  other_routine:
    ret

  ; This funcions is just a stub. Its implementation will be in C
  call_me_maybe:
    nop

  internal_to_asm:
    ret

  asm_main:
    call internal_to_asm
    call call_me_maybe
    ret

Nesse código a rotina ``call_me_maybe`` será implementada em C. O problema é que ela **precisa existir** no código assembly, caso contrário o ``avrasm2`` não será capaz de compilar o codigo e gerar o Intel Hex. Então o que fazemos é compilar o código normalmente, mas podemos remover todo o código da rotina externa, ou até mesmo, posicionar o label em questão em qualquer lugar do código. Por enquanto vamos deixá-lo apenas com uma instrução ``nop``.

Fazemos o processo normal de compilação e `conversão de Intel Hex para avr-elf32 <{filename}convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.rst>`_, o que muda é que agora precisamos reconstruir a tabela de símbolos com dois tipos de símbolos: interno e externo. Nesse caso o único símbolo externo será o ``call_me_maybe``. 

Usaremo as mesmas ferrametas do `último post <{filename}convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.rst>`_, apenas com algumas pequenas mudanças para dar suporte à diferenciação de símbolos internos e externos. Para facilitar, coloquei o nome de todos os símbolos externos direto no código da ferramenta ``extract-symbols-metadata.py`` [#]_. O formato da saída dessa ferramenta também precisou mudar, pois agora temos símbolos internos e externos. O formato ficou assim:

.. code-block:: text

  <symbol_name> <symbol_type> <symbol_address> <instruction_addresses>

Ou seja, agora temos a indicação se o símbolo é interno ou externo (campo ``<symbol_type>``). Assim, quando passamos esse conteúdo para a outra ferramenta, ``elf-add-symbol`` [#]_, ela consegue adicionar corretamente os símbolos que são externos, ou seja, que precisam pertencer à seção ``NULL`` que vimos no início desse post.

Nesse ponto compilamos o código da mesma forma que já fizemos antes. Olhando a tabela de símbolos, depois de já ter convertido de Intel HEX para ``avr-elf32``, temos o seguinte:

.. code-block:: objdump

  Section Headers:
  [  Nr ] Type              Addr     Size     ES Flg Lk Inf Al Name
  [    0] NULL              00000000 00000000 00     00 000 00                   
  [    1] PROGBITS          00000000 00000010 00 AX  00 000 01 .text             
  [    2] STRTAB            00000000 0000002b 00     00 000 01 .shstrtab         
  [    3] SYMTAB            00000000 00000060 10     04 002 04 .symtab           
  [    4] STRTAB            00000000 00000036 00     00 000 01 .strtab           
  [    5] REL               00000000 00000010 08     03 001 04 .rel.text         
  Key to Flags: W (write), A (alloc), X (execute)


  Symbol table (.symtab)
  [  Nr ] Value    Size     Type    Bind      Sect Name
  [    0] 00000000 00000000 NOTYPE  LOCAL        0   
  [    1] 00000000 00000000 SECTION LOCAL        1   
  [    2] 00000000 00000000 NOTYPE  GLOBAL       1 other_routine
  [    3] 00000006 00000000 NOTYPE  GLOBAL       1 asm_main 
  [    4] 00000000 00000000 NOTYPE  GLOBAL       0 call_me_maybe 
  [    5] 00000004 00000000 NOTYPE  GLOBAL       1 internal_to_asm 

Perceba que da mesma forma que observamos o símbolo ``asm_main`` no início desse post, agora vemos que o símbolo ``call_me_maybe`` também está associado à seção ``NULL``.
  
Vamos ver como está o disassembly do código, antes de fazer a link-edição final.

.. code-block:: objdump


  Disassembly of section .text:

  00000000 <other_routine>:
     0:   08 95           ret
          ...

  00000004 <internal_to_asm>:
     4:   08 95           ret

  00000006 <asm_main>:
     6:   0e 94 02 00     call    0x4     ; 0x4 <internal_to_asm>
     a:   0e 94 01 00     call    0x2     ; 0x2 <other_routine+0x2>
     e:   08 95           ret

Olhando a instrução no endereço ``0xa``, que é a linha do código em que a rotina ``call_me_maybe`` é chamada, vemos que a chamda está sendo feita para um endereço incorreto (``0x2``). Mas olhando a tabela de realoção (abaixo), vemos que essa instrução está marcada para ser editada no momento da link-edição. Podemos perceber também que o disassembly acima nem mostra onde está o símbolo ``call_me_maybe``, já que ele é um símbolo externo.

.. code-block:: objdump

  RELOCATION RECORDS FOR [.text]:
  OFFSET   TYPE              VALUE 
  0000000a R_AVR_CALL        call_me_maybe
  00000006 R_AVR_CALL        internal_to_asm

O que essa tabela de realocação diz é que quando o ``avr-gcc`` estiver juntando todos os códigos (C e Assembly) ele sabe que essas duas instruções deverão ser editadas e recebrão o endereço final dos símbolos ``call_me_maybe`` e ``internal_to_asm``, respectivamente. Agora vejamos o código C e como ele fica depois de compilado para ``avr-elf32``.

Código C que usaremos nesse exemplo:

.. code-block:: c

  #include <avr/io.h>

  static int a = 1;


  void call_me_maybe(){
    a += 1;
    if (a > 3){
      return;
    }
    return;
  }

  extern void asm_main();

  int main(){
    
    asm_main();
      
    DDRB = DDRB | _BV(PB5); // PIN13 (internal led) as output
    PORTB = PORTB | _BV(PB5); // HIGH
    
    return 0;
  }

Olhando a tabela de símbolos temos:

.. code-block:: objdump

  Section Headers:
  [  Nr ] Type              Addr     Size     ES Flg Lk Inf Al Name
  [    0] NULL              00000000 00000000 00     00 000 00                   
  [    1] PROGBITS          00000000 00000014 00 AX  00 000 01 .text       <-----      
  [    2] RELA              00000000 00000030 0c     09 001 04 .rela.text        
  [    3] PROGBITS          00000000 00000002 00 WA  00 000 01 .data             
  [    4] NOBITS            00000000 00000000 00 WA  00 000 01 .bss              
  [    5] PROGBITS          00000000 0000000e 00 AX  00 000 01 .text.startup     
  [    6] RELA              00000000 0000000c 0c     09 005 04 .rela.text.startup 
  [    7] PROGBITS          00000000 00000028 01     00 000 01 .comment          
  [    8] STRTAB            00000000 0000004d 00     00 000 01 .shstrtab         
  [    9] SYMTAB            00000000 00000110 10     0a 00d 04 .symtab           
  [   10] STRTAB            00000000 00000069 00     00 000 01 .strtab           
  Key to Flags: W (write), A (alloc), X (execute)


  Symbol table (.symtab)
  [  Nr ] Value    Size     Type    Bind      Sect Name
  [    0] 00000000 00000000 NOTYPE  LOCAL        0   
  [    1] 00000000 00000000 FILE    LOCAL    65521 main.c 
  [    2] 00000000 00000000 SECTION LOCAL        1   
  [    3] 00000000 00000000 SECTION LOCAL        3   
  [    4] 00000000 00000000 SECTION LOCAL        4   
  [    5] 0000003e 00000000 NOTYPE  LOCAL    65521 __SP_H__ 
  [    6] 0000003d 00000000 NOTYPE  LOCAL    65521 __SP_L__ 
  [    7] 0000003f 00000000 NOTYPE  LOCAL    65521 __SREG__ 
  [    8] 00000000 00000000 NOTYPE  LOCAL    65521 __tmp_reg__ 
  [    9] 00000001 00000000 NOTYPE  LOCAL    65521 __zero_reg__ 
  [   10] 00000000 00000002 OBJECT  LOCAL        3 a 
  [   11] 00000000 00000000 SECTION LOCAL        5   
  [   12] 00000000 00000000 SECTION LOCAL        7   
  [   13] 00000000 00000014 FUNC    GLOBAL       1 call_me_maybe     <-----
  [   14] 00000000 0000000e FUNC    GLOBAL       5 main 
  [   15] 00000000 00000000 NOTYPE  GLOBAL       0 asm_main 
  [   16] 00000000 00000000 NOTYPE  GLOBAL       0 __do_copy_data 

Vemos que ele declara o simbolo ``call_me_maybe`` como sendo pretencente à seção ``.text``, que é o correto pois para o código C esse símbolo é um símbolo interno.

Vale notar que esse código C também possui símbolos externos, como por exemplo o símbolo ``asm_main``. Pelo fato de estarmos com o "main" feito em C e estarmos testanto a chamada Assembly->C precisamos, de alguma forma, fazer com que o código C chame nosso código Assembly e é isso que fazemos quando o código C faz ``asm_main()``. Nesse exemplo que estamos fazendo estamos testando os dois caminhos de chamada, tanto C->Assembly quando Assembly->C.


Juntando tudo em um binário final
=================================


Agora que já temos nossos dois ``avr-elf32`` preparados e com suas tabelas de símbolos e realocação criadas, precisamos pedir ao compilador que junte tudo em um único binário, que poderemos gravar na memória do micro-controlador para ser executado.

Esse paso, a link-edição (junto com a compilação), é feita normalmente com o ``avr-gcc``, com uma linha de comando semelhante a essa:

.. code-block:: shell

  avr-gcc -mmcu=atmega328p -F_CPU=100000 -o final_elf.elf main.c elf_from_asm_code.elf

Onde o ``main.c`` é nosso código C e ``elf_from_asm_code.elf`` é nosso código assembly que foi compilado pelo ``avrasm2``, convertido para ``avr-elf32`` e teve suas tabelas de símbolo e realocação reconstruídas. Juntando esses dois binários teremos no final o arquivo ``final_elf.elf``, já com todos os símbolos resolvidos e endereços de instruções editados pelo compilador.

Vejamos então como fica o desassembly desse binário final:

.. code-block:: objdump

  00000096 <call_me_maybe>:
    96:   80 91 00 01     lds     r24, 0x0100
    9a:   90 91 01 01     lds     r25, 0x0101
    9e:   01 96           adiw    r24, 0x01       ; 1
    a0:   90 93 01 01     sts     0x0101, r25
    a4:   80 93 00 01     sts     0x0100, r24
    a8:   08 95           ret

  000000aa <_other_routines>:
    aa:   00 00           nop
          ...

  000000ae <internal_to_asm>:
    ae:   08 95           ret

  000000b0 <asm_main>:
    b0:   0e 94 57 00     call    0xae    ; 0xae <internal_to_asm>
    b4:   0e 94 4b 00     call    0x96    ; 0x96 <call_me_maybe>
    b8:   08 95           ret

  000000ba <main>:
    ba:   0e 94 58 00     call    0xb0    ; 0xb0 <asm_main>
    be:   25 9a           sbi     0x04, 5 ; 4
    c0:   2d 9a           sbi     0x05, 5 ; 5
    c2:   80 e0           ldi     r24, 0x00       ; 0
    c4:   90 e0           ldi     r25, 0x00       ; 0
    c6:   08 95           ret



Podemos perceber aqui que o código pertencente à rotina ``cal_me_maybe`` (com posição final no endereço ``0x00000096``) é de fato o código que está no ``main.c`` e não o simples ``nop`` que deixamos no código assembly orignal. Ou seja, conseguimos sobrescrever a rotina feita em assembly por um código implementado em C.

Podemos observar também que as chamadas estão corretas. O compilador corrigiu todos os endereços que apontavam para a rotina ``cal_me_maybe``. Lembram do ``call 0x2`` que tínhamos no elf que veio do assembly? Ele foi corretamente editado e agora aponta para o enreço ``0x96``, que é exatamente o endereço da rotina ``call_me_maybe``.

Agora o que temos que fazer é gravar esse código final na memória do micro-controlador. E o melhor de tudo é que ele funciona!!


.. [#] `ElfIO - C++ library for reading and generating ELF files <http://elfio.sourceforge.net/>`_
.. [#] `extract-symbols-metadata <{filename}/extra/extract-symbols-metadata-v2.py>`_
.. [#] `Código-fonte da ferramenta elf-add-symbol <{filename}/extra/elf-add-symbol-v2.cpp>`_
