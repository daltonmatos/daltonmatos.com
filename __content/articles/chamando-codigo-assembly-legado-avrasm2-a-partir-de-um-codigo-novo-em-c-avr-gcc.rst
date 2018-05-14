:title: Chamando código Assembly legado (AVRASM2) a partir de um código novo em C (avr-gcc)
:author: Dalton Barreto
:date: 2015-04-12
:lang: pt
:tags: avr, microcontrollers, avr-C, avr-assembly
:slug: chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc
:status: published

Contexto
========

Todos os tutoriais que encontrei na internet que falam sobre mistura de C e ASM em um mesmo projeto ensinam a fazer da mesma forma, que é usando ``avr-gcc``. O problema comum em todos eles é que assumem que você está começando um projeto do zero. Isso significa que o código assembly deve estar na sintaxe que o ``avr-as`` (GNU Assembler) espera encontrar. Quando me refiro a "código legado" estou falando de Assembly feito no AVR Studio, usando o AVRASM2 como Assembler. A sintaxe do Assembly que o ``AVRASM2`` espera é incompatível com a que o ``avr-as`` espera, então não podemos simplesmente pegar o código e compilar com ``avr-as``.

Dependendo do tamanho do projeto original é inviável migrar tudo de um vez e é aí que poder mesclar C e ASM se torna muito útil, pois você pode ir escrevendo o código C ao mesmo tempo em que o sistema está evoluindo e eventualmente ganhando novas funcionalidades. O desafio desse post é conseguir juntar dois projetos que foram feitos usando ferramentas diferentes (``avr-gcc`` e ``AVR Studio``) que, a princípio, são incompatíveis.

Muitos desses projetos ASM (todos?) feitos há muito tempo atrás provavelmente foram feitos com assemblers que não tinham em mente a junção com código C e portanto geram binários que não possuem suporte à link-edição e outras coisas necessárias para que possamos juntar as duas linguagens. Esse é o caso do ``AVR Studio`` (quando usando ``AVRASM2`` como Assembler), ele gera no final do build um arquivo no formato Intel Hex [#]_, que não possui, dentre outras coisas, suporte à link-edição.


Preparação dos arquivos
=======================

Antes de podermos começar precisamos ter todos os nossos arquivos em um mesmo formato, para que possamos usar o ``avr-gcc`` para gerar nosso binário final. Isso significa que teremos que converter todos os arquivos para um formato que o ``avr-gcc`` entenda. 

Como o AVRASM2 gera Intel Hex (HEX) temos que converter esse conteúdo para elf32-avr (ELF), assim poderemos juntar esse código com nosso código compilado pelo ``avr-gcc``. Não existe uma conversão direta de HEX pra ELF, o que podemos fazer é converter de HEX para flat binary e depois para ELF. A conversão é feita com ``avr-objcopy``.


Exemplo de código AVRASM2 
=========================

Vamos pegar um pequeno exemplo de código feito com AVRASM2 para podermos fazer o processo completo.

.. code-block:: asm
  
      .include "m328Pdef.inc"

      .org 0x0000

      _blinks:
        ldi r23, 0xa
        add r24, r23
        clr r1
        clr r25
        ret 

Esse código apenas soma o valor 10 ao parametro que ele receber. A linha do ``.include`` é necessária pois é nela que existem as definiçoes de resgitradores e etc para o micro controlador que estivermos usando. Nesse caso estamos usando um ATmega328P, mas poderia ser qualquer outro AVR. Importante notar a instrução ``.org 0x0000``, isso faz com que nosso código seja posicionado no endereço de memória ``0``. Precisaremos saber disso mais adiante.

O HEX gerado pelo AVRASM2 (AVRStudio 4, por exemplo) possui apenas um seção chamada ``.sec1``, então só precisamos copiá-la pra o flat binary.

.. code-block:: objdump

      $ avr-objdump -h blinks.hex

      blinks.hex:     file format ihex

      Sections:
      Idx Name          Size      VMA       LMA       File off  Algn
        0 .sec1         0000000a  00000000  00000000  00000011  2**0
                        CONTENTS, ALLOC, LOAD


Copiando essa seção para o flat binary:

.. code-block:: shell-session

      $ avr-objcopy -j .sec1 -I ihex -O binary blinks.hex blinks.bin


Agora precisamos converter para ELF:

.. code-block:: shell-session

      $ avr-objcopy  --rename-section .data=.progmem.data,contents,alloc,load,readonly,data \
      -I binary -O elf32-avr blinks.bin blinks.elf

Nesse momento temos um código asembly já pronto para ser link-editado com qualquer outro código gerado pelo avr-gcc. Mas ainda temos alguns problemas. 
Olhando o arquivo ELF de perto, vemos que o símbolo ``_blinks`` não está na tabela de símbolos e precisamos saber onde nossa rotina começa para podermos referenciá-la no código C.

.. code-block:: objdump

  $ avr-objdump -x blink_simple.asm.elf

  blink_simple.asm.elf:     file format elf32-avr

  SYMBOL TABLE:
  00000000 l    d  .progmem.data	00000000 .progmem.data
  00000000 g       .progmem.data	00000000 _binary_blinks_bin_start
  0000000a g       .progmem.data	00000000 _binary_blinks_bin_end
  0000000a g       *ABS*	        00000000 _binary_blinks_bin_size


Os três símobolos ``_binary_*`` foram criados pelo ``avr-objcopy`` e marcam, respectivamente, o início, fim e tamanho total do nosso código, depois de compilado. Mesmo não tendo o símbolo ``_blinks`` podemos deduzir onde ele está. Se voltarmos no código assembly veremos que a instrução ``.org 0x0000`` está lá e sabemos que ela força o posicionamento do ínício do nosso código no endereço ``0``. Então podemos usar o símbolo ``_binary_blinks_bin_start`` como sendo nosso ponto de entrada no código assembly.

Analisando o código em C
========================

Para validar nossa hipótese, vamos fazer um código em C que chama essa rotina escrita em Assembly. O código é bem simples, tudo que ele faz é piscar o LED que está ligado na porta D13. Como esse código foi testando em um Arduino Nano, a porta D13 é, na verdade, o bit 5 da PORTB [#]_.


.. code-block:: c

  #include <avr/io.h>
  #include <util/delay.h>

  // Arduino Pin13 is mapped to PORTB, bit 5
  // See: http://www.arduino.cc/en/Reference/PortManipulation

  extern char ASM_SYM(char n);

  int main(void){

    uint8_t total_blinks =  ASM_SYM(5);
    DDRB = DDRB | _BV(PB5); // PIN13 (internal led) as output

    PORTB = PORTB | _BV(PB5); // HIGH 
    for (;;){
      uint8_t i;
      for (i = 0; i < total_blinks; i++){
        PORTB = PORTB | _BV(PB5); // HIGH
        _delay_ms(200);

        PORTB &= ~_BV(PB5); // LOW
          _delay_ms(200);
      }
      _delay_ms(1000);
    }

    return 0;
  }

        

Como vamos usar esse mesmo código para linkar com vários códigos ASM diferentes, deixamos o nome da função como uma constante (``ASM_SYM``) e vamos passar um valor para essa constante para o ``avr-gcc``, no momento de compilar esse código.

Compilando tudo e juntando em um mesmo binário
==============================================

A compilação do código em C é simples, nada demais em relação aqualquer outra compilação:

.. code-block:: shell-session

  $ avr-gcc -mmcu=atmega328p -Os -DF_CPU=16000000 -DASM_SYM=_binary_blinks_bin_start -o main.elf main.c blinks.elf


Podemos olhar o ELF gerado para saber se o código parece correto:

.. code-block:: shell-session

  $ avr-objdump -d main.elf


.. code-block:: objdump


  Disassembly of section .text:

  00000000 <__vectors>:
     0:	0c 94 34 00 	jmp	0x68	; 0x68 <__ctors_end>
     4:	0c 94 3e 00 	jmp	0x7c	; 0x7c <__bad_interrupt>

  00000068 <__ctors_end>:
    68:	11 24       	eor	r1, r1
    6a:	1f be       	out	0x3f, r1	; 63
    6c:	cf ef       	ldi	r28, 0xFF	; 255
    6e:	d8 e0       	ldi	r29, 0x08	; 8
    70:	de bf       	out	0x3e, r29	; 62
    72:	cd bf       	out	0x3d, r28	; 61
    74:	0e 94 45 00 	call	0x8a	; 0x8a <main>
    78:	0c 94 6d 00 	jmp	0xda	; 0xda <_exit>

  0000007c <__bad_interrupt>:
    7c:	0c 94 00 00 	jmp	0	; 0x0 <__vectors>

  00000080 <_binary_blinks_bin_start>:
    80:	7a e0       	ldi	r23, 0x0A	; 10
    82:	87 0f       	add	r24, r23
    84:	11 24       	eor	r1, r1
    86:	99 27       	eor	r25, r25
    88:	08 95       	ret

  0000008a <main>:
    8a:	80 e0       	ldi	r24, 0x00	; 0
    8c:	0e 94 40 00 	call	0x80	; 0x80 <_binary_blinks_bin_start>
    90:	25 9a       	sbi	0x04, 5	; 4
    92:	2d 9a       	sbi	0x05, 5	; 5



Algumas partes do código foram omitidas para podermos nos concentrar no que é importante. O que temos que observar aqui é onde está nosso código ASM, que nesse caso está no endereço ``0x0080``. Olhando o código da nossa função ``main`` vemos que a segunda instrução é o ``call 0x80``, que é justamente a chamada à nossa rotina Assembly.

Nesse ponto, temos um ELF que precisamos converter de volta para HEX, para que possamos fazer o flash para o micro controlador.

.. code-block:: shell-session

  $ avr-objcopy -I elf32-avr -O ihex -j .text -j .data main.elf main.hex


De fato, esse é um exemplo muito simples e provavelmente não representa uma situação real em que temos um projeto Assembly legado que precisa ser migrado para C. Pensando nisso, vamos analisar exemplos mais complexos de código Assembly que fazem uso de outras instruçoes como ``jmp, call, rjmp``.


Analisando um código que usa jmp
================================

Agora vamos fazer o mesmo procedimento mas usando um código Assembly que faz uso da instrução ``jmp``.

.. code-block:: asm

  .org 0x0000

  _blinks:
    jmp _add

  _add:
    clr r1
    clr r25
    ldi r23, 0xa
    add r24, r23
    ret 

O código é basicamente o mesmo, mas forçamos um ``jmp`` apenas para ilustrar nosso problema. Depois que compilamos com o AVRASM2 e geramos o elf temos o seguinte:

.. code-block:: objdump

  Disassembly of section .text:

  00000000 < _binary_blinks_bin_start>:
     0:	0c 94 02 00 	jmp	0x4	; 0x4 < _binary_blinks_bin_start+0x4>
     4:	11 24       	eor	r1, r1
     6:	99 27       	eor	r25, r25
     8:	7a e0       	ldi	r23, 0x0A	; 10
     a:	87 0f       	add	r24, r23
     c:	08 95       	ret


Olhando o assembly gerado, vemos que está tudo certo pois nosso código começa e ``0x0000`` e o jmp está indo para o endereço ``0x0004``, que é onde começa nossa rotina ``_add``. Sabemos disso pois a instrução ``clr r1, r1`` é traduzida para ``eor r1, r1``. Agora é hora de juntar isso ao noso código C. Vejamos o Assembly final:

.. code-block:: objdump

  Disassembly of section .text:

  00000000 <__vectors>:
     0:	0c 94 34 00 	jmp	0x68	; 0x68 <__ctors_end>
     4:	0c 94 3e 00 	jmp	0x7c	; 0x7c <__bad_interrupt>
     8:	0c 94 3e 00 	jmp	0x7c	; 0x7c <__bad_interrupt>

  00000068 <__ctors_end>:
    68:	11 24       	eor	r1, r1
    6a:	1f be       	out	0x3f, r1	; 63
    6c:	cf ef       	ldi	r28, 0xFF	; 255
    6e:	d8 e0       	ldi	r29, 0x08	; 8
    70:	de bf       	out	0x3e, r29	; 62
    72:	cd bf       	out	0x3d, r28	; 61
    74:	0e 94 47 00 	call	0x8e	; 0x8e <main>
    78:	0c 94 6f 00 	jmp	0xde	; 0xde <_exit>

  00000080 <_binary_blinks_bin_start>:
    80:	0c 94 02 00 	jmp	0x4	; 0x4 <__zero_reg__+0x3>
    84:	11 24       	eor	r1, r1
    86:	99 27       	eor	r25, r25
    88:	7a e0       	ldi	r23, 0x0A	; 10
    8a:	87 0f       	add	r24, r23
    8c:	08 95       	ret

  0000008e <main>:
    8e:	80 e0       	ldi	r24, 0x00	; 0
    90:	0e 94 40 00 	call	0x80	; 0x80 < _binary_blinks_bin_start>
    94:	25 9a       	sbi	0x04, 5	; 4

Olhando o código da nossa função ``main()`` vemos que o call é feito corretamente para o endereço ``0x0080``, mas quando olhamos para o código de nossa rotina Assembly, em ``0x0080``, vemos que o endereço para onde o ``jmp`` está indo continua sendo ``0x4`` e olhando esse endereço percebemos que certamente não é o endereço correto. Isso acontece pois o código Assembly foi compilado completamente separado do código C e não tem nehuma ideia de que vai, na verdade, ser inserido no meio de um outro binário e que por isso deveria ter seus endereços ajustados.

O endereço correto para onde o ``jmp`` deveria ir é ``0x0084``. Precisamos fazer, de alguma forma, esses endereços ficarem certos. Uma forma bem "suja" de se fazer isso é "deslocar" o código assembly em exatamente ``0x0080``. Afinal, sabemos que ele será posicionado no endereço ``0x0080`` (vimos isso no disassembly do ELF). Mudando a instrução ``.org 0x0000`` para ``.org 0x0080`` temos o seguinte no diassembly do ELF final.

.. code-block:: objdump

  00000080 <_binary_blinks_bin_start>:
    80:	0c 94 82 00 	jmp	0x104	; 0x104 <_etext+0x22>
    84:	11 24       	eor	r1, r1
    86:	99 27       	eor	r25, r25
    88:	7a e0       	ldi	r23, 0x0A	; 10
    8a:	87 0f       	add	r24, r23
    8c:	08 95       	ret

Percebemos que o endereço final ainda ficou errado. Mas vamos parar um pouco e analisar como nossa instrução de ``jmp`` foi codificada. Analisando a linha isoladamente temos o segunte:

.. code-block:: objdump


    80:	0c 94 82 00 	jmp	0x104	; 0x104 <_etext+0x22>

O que temos aqui é o código da instrução ``oc 94`` e o endereço para onde o ``jmp`` deve ir, nesse caso ``82 00``. Quando compilamos nosso código com o avrasm2 podemos gerar um arquivo adicional que contem todos os labels originais do assembly (opção ``-m``) e seus endereços finais. Olhando esse arquivo temos o seguinte:

.. code-block:: shell-session

  CSEG _blinks      00000080
  CSEG _add         00000082

isso nos diz que nossa rotina ``_add`` está exatamente no endereço ``0082`` que é o mesmo endereço que vemos na codificação da nossa instrução (``0c 94 82 00``) do ELF, eles estão apenas representados de forma diferente [#]_.

Nossa rotina que estava originalmente no endereço ``0082`` está com o jmp para ``0x104``. Mas ``0x104`` é exatamente o dobro de ``0x0082`` então vamos trocar o nosso ``.org 0x0080`` para ``.org 0x0040`` e ver o que acontece.


.. code-block:: objdump

  00000080 <_binary_blinks_bin_start>:
    80:	0c 94 42 00 	jmp	0x84	; 0x84 <_binary_blinks_bin_start+0x4>
    84:	11 24       	eor	r1, r1
    86:	99 27       	eor	r25, r25
    88:	7a e0       	ldi	r23, 0x0A	; 10
    8a:	87 0f       	add	r24, r23
    8c:	08 95       	ret

Agora sim temos o ``jmp`` para o endereço correto! Não sei ao certo porque isso funciona mas parece dar certo. Funciona inclusive pra um código assembly em que fazemos uso de várias instruçoes de desvio ao mesmo tempo (``jmp``, ``rjmp``, ``call``):

.. code-block:: asm

  _blinks:
    rjmp _add
  _ret:
    ret
   
  _add:
    call _ldi
  _add1:
    add r24, r23
    call _clear
    rjmp _ret

  _clear:
    clr r1
    clr r25
    ret
    
  _ldi:
    ldi r23, 0x5
    jmp _add1 

Diassembly do ELF final:

.. code-block:: objdump

  00000080 <_binary_blinks_bin_start>:
    80:	01 c0       	rjmp	.+2      	; 0x84 <_binary_blinks_bin_start+0x4>
    82:	08 95       	ret
    84:	0e 94 4b 00 	call	0x96	; 0x96 <__binary_blinks_bin_start+0x16>
    88:	87 0f       	add	r24, r23
    8a:	0e 94 48 00 	call	0x90	; 0x90 <__binary_blinks_bin_start+0x10>
    8e:	f9 cf       	rjmp	.-14     	; 0x82 <__binary_blinks_bin_start+0x2>
    90:	11 24       	eor	r1, r1
    92:	99 27       	eor	r25, r25
    94:	08 95       	ret
    96:	75 e0       	ldi	r23, 0x05	; 5
    98:	0c 94 44 00 	jmp	0x88	; 0x88 <__binary_blinks_bin_start+0x8>



Conclusoes
==========

Vimos que é possível gerar um HEX, converter pra ELF e chamar uma rotina Assembly que está dentro desse binário. Mas isso é só o início, ainda temos um longo caminho pela frente até podermos pegar um projeto Assembly realmente grande (10K+ LOC) e mesclar com C.

Quando misturamos C e Assembly existem regras que devemos obedecer no momento de usar os registradores. Essas regras estão descritas nesse documento da Atmel [#]_. Antes de tentar reproduzir o que fizemos aqui em um projeto Assembly maior e com funcionalidades reais certifique-se de que o uso dos registradores está em conformidade com essas regras ou as chamadas ao código assembly podem simplesmente não funcionar.


Trabalhos futuros
=================

Ainda tenho muita pesquisa para fazer e algumas hipóteses para confirmar, mas isso é assunto para alguns próxmos posts. Isso inclui:

* Como inserir simbolos na tabela de simbolos dos ELFs gerados. Isso nos daria a possibilidade de chamar rotinas que estão "no meio" do código Assembly;
* Como trabalhar com relocação de simbolos. Quando vemos o disassembly de um ELF gerado em um projeto C+Assembly feito com ``avr-gcc`` vemos que os simbolos do código assembly são adicionados em uma seção especial do ELF chamada Relocation table. Sabendo manipular esse tabela pode ser que se torne bem mais fácil o uso de código assembly, sem precisar por exemplo desse hack da instrução ``.org`` que precisamos fazer;
* Descobrir como fazer a chamada no sentido contrário, ou seja, código assembly legado chamando código novo C. O que fizemos aqui foi apenas código C chamando código Assembly.

Obrigado pela leitura e fique ligado em posts futuros sobre esse assunto. Ainda tenho muita pesquisa para fazer sobre isso.

Próximo post: `Convertendo Intel HEX para ELF32-avr criando tabela de símbolos e tabela de realocação <{filename}convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.rst>`_.


.. [#] `Intel Hex Format <http://en.wikipedia.org/wiki/Intel_HEX>`_
.. [#] `Port Registers - Arduino.cc <http://www.arduino.cc/en/Reference/PortManipulation>`_
.. [#] `Endianness <http://en.wikipedia.org/wiki/Endianness>`_
.. [#] `Mixing Assembly and C with AVRGCC - Atmel Corporation <http://www.atmel.com/images/doc42055.pdf>`_
