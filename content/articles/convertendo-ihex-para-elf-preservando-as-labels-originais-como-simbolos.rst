:title: Convertendo Intel HEX para ELF32-avr criando tabela de símbolos e tabela de realocação
:author: Dalton Barreto
:date: 2015-04-17
:status: published
:slug: convertendo-intel-hex-para-elf32-avr-mantendo-tabela-de-simbolos-e-tabela-de-realocacao


Esse post faz parte de uma `série de posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ sobre mistura de código C (avr-gcc) com código Assembly (AVRASM2). Se você ainda não leu os posts anteriores, recomendo que leia antes de prosseguir.

Contexto
========

No `post anterior <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ vimos que é possível chamar código assembly (feito com AVRASM2) a partir de codigo C (avr-gcc). Vimos também que existem algumas limitaçoes na estratégia usada, tivemos que ajustar a instrução ``.org`` e isso significa que tínhamos que ajustar o código assembly toda vez que adicionávamos mais código C. Nesse post vamos ver uma outra abordagem em que isso não é mais necessário.

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

Vamos analisar esse código mais de perto e ver o que está acontecendo. Vemos que nosso código assembly foi posicionado no endereço ``0x0080`` e que nossa funcção ``main()`` faz uma chamada a esse endereço (``call 0x80``).

Olhando as duas primeiras instruçoes de nossa rotina Assembly (``_binary_build_blink_call_asm_bin_start``), vemos que as duas chamadas estão indo para endereços completamente errados (``0x10`` e ``0xa``). É fácil perceber que os endereços corretos deveriam ser, respectivamente, ``0x90`` e ``0x8a``. Até aqui nenhuma novidade em relação ao que já fizemos. Acontece que podemos mostrar ao compilador onde cada uma de nossas rotinas começa e fazemos isso atráves da tabela de símbolos [#]_.

Manipulando a tabela de símbolos
================================


A tabela de símbolos diz ao compilador onde está cada parte do nosso código, no nosso caso, onde estão cada uma das rotinas assembly. Vamos voltar um pouco e olhar a tabela de símbolos do nosso código assembly compilado, recém convertido para ELF partir de um HEX. Se olharmos bem veremos que só temos os símbolos criados pelo ``avr-objcopy`` quando fizemos a conversão.

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

(Lembrando que nesse disasembly as duas primeiras instruçoes estão corretas pois o código ainda não foi linkado com o código C)

Quando convertemos um HEX para ELF perdemos todas as labels (símbolos) originais do Assembly. Na verdade, só de compilar o Assembly as labels já são convertidas em endereços absolutos.

Acontece que o ``avrasm2`` pode gerar, no momento da compilação, dois arquivos adicionais: Um tem todos os labels e seus endereços finais (``.map, opção -m``) e o outro tem o código assembly final, ainda em formato de texto mas já com todos os endereços resolvidos (``.lst, opção -l``). Olhando o ``.lst`` vemos como ficou nossa rotina ``_blinks``:

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


Podemos perceber que a linha do ``jmp`` é codificada como ``940e 0008``. A primeira parte é o código da instrução e a segunda é o endereço para onde ela transfere o controle da execução.

No aquivo que contém todos as labels e seus respectivos endereços finais, temos o seguinte:


.. code-block:: text

  CSEG _blinks      00000000
  CSEG _clear       00000008
  CSEG _real_code   00000005

Aqui temos nossos três símbolos: ``_blinks``, ``_clear`` e ``_real_code``. Olhando o disassembly do arquivo ELF vemos que a primeira instrução ``jmp`` foi codificada como: ``0e 94 08 00``, que é essencialmente a mesma coisa que tínhamos no nosso arquivo ``.lst``!

ELF:

.. code-block:: objdump

  00000000 <_blinks>:
     0:	0e 94 08 00 	call	0x10	; 0x10 <_binary_build_blink_call_asm_bin_start+0x10>

.lst:

.. code-block:: text

                   _blinks:
  000000 940e 0008   call _clear
                   

A única diferença entre eles parece ser a representação do bit mais significativo [#]_. No ELF a representação está com o byte menos significativo primeiro (mais à esquerda) e no ``.lst`` está com byte menos signifcativo por último (mais à diretia). Isso significa que nossa rotina ``_clear`` que no HEX estava no endereço ``0x0008`` está agora no ELF no endereço ``0x10``.

Ainda não entendo porque o código da instrução menciona o endereço ``0008`` e o disassembly mostra ``jmp 0x10`` (um é o dobro do outro!), mas percebi que a princípio os endereços sempre coincidem! Ou seja, no ELF os endereços são sempre o dobro dos respectivos endereços no HEX. Talvez isso tenha relação com como o ELF representa internamente as instruçoes. A instrução que vai para o AVR é mesmo ``0e 94 08 00``, ou seja, o ``jmp`` irá saltar para o endereço ``0008`` da memória flash do AVR, mas como estamos adicionando símbolos no ELF, precisamos obeceder o endereçamento que ele mostra.

Agora que sabemos onde estão nossas duas rotinas (``_clear`` e ``_real_code``) dentro do ELF podemos adicionar dois símoblos à tabela de símbolos. Como não encontrei nenhuma ferramenta que adicionasse símbolos a um ELF, escrevei meu pŕoprio código [#]_ que faz isso, chamei a ferramenta de ``elf-add-symbol``. Nossa nova tabela de símbolos ficou assim (mais detalhe em como ela foi adicionada ao arquivo ELF: `Automatizando todo o processo`_):

.. code-block:: text

  SYMBOL TABLE:
  00000000 l    d  .text	00000000 .text
  00000000 g       .text	00000000 _blinks
  00000010 g       .text	00000000 _clear
  0000000a g       .text	00000000 _real_code

A tabela é simples. Temos o endereço do símbolo, a seção do ELF onde ele está, o tamanho do símbolo e o nome do símbolo. O ``g`` e ``l`` significam, respectivamente, Símbolo Global e Símbolo Local. Isso é importante pois apenas símbolos globais são enxergados no momento da link-edição.
  
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

Isso já ajuda, mas quando linkamos esse código Assembly com código C, mesmo tendo manipulado a tabela de símbolos (que já é um bom começo) ainda ficamos com endreços errados. Vejamos o disassembly após a link-edição:


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


Perceba que todo nosso codigo Assembly foi posicionado no endereço ``0x0080`` e mesmo nossas duas rotinas auxiliares tendo sido posicionadas, respectivcamente, em ``0x008a`` e ``0x0090`` as duas linhas com as chamadas ``call`` continuam achando que as rotinas estão em ``0x10`` e ``0xa``. É aí que entra a tabela de realocação. 

Isso acontece porque esse código assembly é apenas **copiado** para alguma posição dentro do binário final durante o processo de link-edição. Precisamos então, de alguma forma, dizer ao compilador que o endereço das rotinas ``_real_code`` e ``_clear`` irá mudar e por isso ele deve ajustar o endereço de chamada de quaisquer instruçoes que fizerem referências a essas rotinas.

Tabela de realocação
====================

A Tabela de realocação [#]_ existe exatamente para dizer ao compilador quais símbolos mudarão de lugar e quais instruçoes ele deve editar e trocar o endereço final.

Para entendermos a tabela de realocação precisamos voltar ao nosso disassembly inicial, antes de ser link-editado ao código C.

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


(Usando a mesma ferramenta [3]_ que escrevi para manipular a tabela de símbolos podemos construir a tabela de realocação)

Vejamos a tabela em detalhes (mais detalhes em como ela foi adicionada: `Automatizando todo o processo`_):

.. code-block:: text

  RELOCATION RECORDS FOR [.text]:
  OFFSET   TYPE              VALUE 
  00000000 R_AVR_CALL        _clear
  00000004 R_AVR_CALL        _real_code


A tabela funciona da segunte forma: Cada seção do ELF pode ter sua tabela de realocação. Nesse caso, essa tabela de realocação "pertence" à secão ``.text``, ou seja, ela faz referência apenas a símbolos que existem na seção ``.text``, que é onde estão as instruçoes do nosso código. O campo ``OFFSET`` indica o endereço da instrução que deverá ser editada (veremos isso em detalhe mais adiante). O campo ``TYPE`` indica o tipo de realocação [#]_, confesso que olhei esse valor (``R_AVR_CALL``) em um ELF gerado pelo avr-gcc (mais sobre isso: `Engenharia reversa para descobrir o valor do R_AVR_CALL`_). O campo ``VALUE`` indica qual símbolo será realocado.

Agora vamos analisar cada uma das linhas da tabela de realocação:

.. code-block:: text

  00000000 R_AVR_CALL        _clear

Essa linha nos diz que a instrução que está na posição ``0x0000`` (``call 0x10``) está fazendo uma chamada a um rotina de nome ``_clear`` e que essa rotina estará em algum lugar no binário final. Seja qual for esse lugar, essa instrução ``call`` deve ser editada e o valor ``0x10`` deve ser trocado pelo endereço final da rotina ``_clear``.

O mesmo acontece pra a outra linha:

.. code-block:: text

  00000004 R_AVR_CALL        _real_code

Aqui é exatamente a mesma coisa, mas a instrução que será editada é o ``call 0xa`` e o ``0xa`` será trocado pelo endereço final da rotina ``_real_code``.

Agora que temos um ELF com tabela de símbolos e tabela de realocação estamos prontos para re-linkar com o código C. Fazendo isso temos o seguinte dissasembly: 

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

E agora temos nosso código assembly com o endereços dos calls corretamente ajustados!

Um detalhe importante é perceber que a instrução foi mesmo editada. Olhando a primeira instrução ``call`` ela está codificada como ``0e 94 48 00`` (antes era ``0e 94 08 00``, lembra?) e como os endereços no ELF são sempre o dobro dos endereços no HEX podemos conferir que ``0x90`` (endereço da rotina ``_clear`` no ELF) é exatamente o dobro de ``0x48``, que é o endereço que está codificado na instrução!!

Esse código funciona quando gravado na memória flash do micro controlador!


Automatizando todo o processo
=============================

É claro que o que fizemos aqui foi uma análise manual de como construir todo o aparato necessário para que possamos realocar rotinas que estão espalhadas pelo nosso código Assembly legado, mas quando estamos lidando com um projeto grande precisamos fazer isso de forma automatizada. Para isso eu escrevi um script que me ajuda a manipular a tabela de símbolos e a tabela de realocação.

Primeiro escrei um script python [#]_ que funciona da segunte maneira:

Dado o conteudo do arquivo de mapa (``.map`` produzido pelo ``avrasm2``) e a saída do disassembly do ELF ele consegue encontrar o novo endereço dos símbolos dentro do ELF e também quais instruçoes possuem desvio para endereços absolutos e, portanto, precisarão ser editadas. Usando esse script com o código que analisamos nese post, temos a seguinte saída:

.. code-block:: shell-session


  > avr-objdump -d blink_call.asm.elf | python2 extract-symbols-metadata.py blink_call.asm.map
  _blinks 0x0000
  _clear 0x10 0x0
  _real_code 0xa 0x4

Olhando bem para essa saída ela representa **exatamente** nossa tabela de realocação. Essa saida é estruturada da segunte forma:

.. code-block:: text

 <nome_do_símbolo> <endereço_do_símbolo> <endereço_das_instruçoes_que_usam_esse_símbolo>

Agora o que precisamos fazer é transformar essa saída em uma tabela de realocação, dentro o ELF. Para isso usamos a ferramenta ``elf-add-symbol`` [3]_. Assumindo que gravamos esse conteudo em ``blink_call.asm.symtab`` podemos fazer o seguinte:

.. code-block:: shell-session

  cat blink_call.asm.symtab | ./elf-add-symbol blink_call.asm.elf

Essa chamada modifica o arquivo ``blink_call.asm.elf`` adicionando a tabela de símbolos e a tabela de realocação! E então estamos prontos para link-editar nosso ELF com nosso código C.




Engenharia reversa para descobrir o valor do R_AVR_CALL
=======================================================

A tabela de realocação tem a uma `estrutura espefícia <http://wiki.osdev.org/ELF_Tutorial#Relocation_Sections>`_. Um dos campos dessa estrutura é o ``r_info``. Esse campo diz duas coisas: Qual o símbolo está sendo realocado (8 bits mais significativos) e qual o tipo de realocação será feita (8 bits menos significativos). Quando escrevi o ``elf-add-symbol``, na biblioteca que usei (ELFIO [#]_) só existiam constantes para os tipos de realocação do ELF32 para arquitetura x86 então, de alguma forma, eu precisava descobrir qual o valor eu deveria colocar nesse campo para a realocação de símbolos para AVR.

O que fiz foi compilar um arquivo assembly com o ``avr-gcc`` e usando a ferramenta ``avr-readelf`` consegui ver o seguinte:

.. code-block:: readelf

  Relocation section '.rela.text' at offset 0x100 contains 2 entries:
   Offset     Info    Type            Sym.Value  Sym. Name + Addend
  00000000  00000112 R_AVR_CALL        00000000   .text + a
  00000004  00000112 R_AVR_CALL        00000000   .text + c

Peguei o valor ``0x112`` (campo ``Info``) e usei a macro ``ELF32_R_TYPE()`` da própria lib ELFIO [7]_. O retorno dessa chamada foi ``0x12`` que é ``18`` em decimal. Por isso no código do ``elf-add-symbol`` temos a linha ``#define R_AVR_CALL 18``.

.. [#] `ELF Symbol Table <http://wiki.osdev.org/ELF_Tutorial#The_Symbol_Table>`_
.. [#] `Endianness <http://en.wikipedia.org/wiki/Endianness>`_
.. [#] `Código-fonte da ferramenta elf-add-symbol <{filename}/extra/elf-add-symbol.cpp>`_
.. [#] `ELF Relocation Table <http://wiki.osdev.org/ELF_Tutorial#Relocation_Sections>`_
.. [#] `AVR ELF Relocation Types <https://sourceware.org/git/gitweb.cgi?p=binutils-gdb.git;a=blob;f=include/elf/avr.h;h=115296da404d034d0626ebe57ac2631a6849d239;hb=HEAD#l53>`_
.. [#] `extract-symbols-metadata <{filename}/extra/extract-symbols-metadata.py>`_
.. [#] `ElfIO - C++ library for reading and generating ELF files <http://elfio.sourceforge.net/>`_

