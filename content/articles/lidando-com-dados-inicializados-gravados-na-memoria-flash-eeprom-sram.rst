:title: Lidando com dados gravados na memória flash, EEPROM e SRAM
:date: 2015-09-13
:status: draft
:author: Dalton Barreto
:slug: lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram


Esse post faz parte de uma `série de posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ sobre mistura de código C (avr-gcc) com código Assembly (``avrasm2``). Se você ainda não leu os posts anteriores, recomendo que leia antes de prosseguir.


Contexto
========

Até agora, nos posts anteriores vimos apenas como fazer chamadas de função de uma linguagem para outra, mas uma parte muito importante de qualquer projeto com micro-controladores é a possibilidade de gravar dados na área de memória do chip (memória flash, por exemplo). É bem comum usar essa memória para gravar valores que serão usados pelo código. O mais comum é vermos strings sendo guardadas para uso futuro, mas é perfeitamente possível guardarmos outros valores como constantes, números e até mesmo definição de fontes, no caso de estarmos lidando com displays de LCD.

Além da memória flash, temos duas outras memórias dispońiveis para usar dessa mesma forma. A memória SRAM [#]_ e a EEPROM [#]_. Vamos ver logo abaixo como gravamos/lemos dados dessas três memórias disponíveis nos micro-controladores AVR (pelo menos na maioria deles).


Lendo/Gravando dados na memória SRAM e EEPROM
=============================================

Tanto a memória SRAM quanto a EEPROM possuem posicionamentos fixos em cada chip AVR, isso significa que, independente da lingagem usada, o endereço de leitura/escrita será sempre o mesmo. Isso significa que não precisamos nos preocupar com nenhum tipo de deslocamento de código quando fizermos a link-edição com algum código C. Tanto o ``avr-gcc`` quanto o ``avrasm2`` vão inicializar corretamente os valores iniciais e finais dos endereços dessas duas memórias e o código poderá referenciar esses endereços livremente.


Lendo/Gravando dados na memória Flash
=====================================

O problema começa quando precisamos ler/gravar dados na memória flash. Isso acontece pois as duas instruções que devemos usar para isso, ``LPM`` e ``SPM`` trabalham de uma forma peculiar, que explico a seguir:

Quando usamos quaisquer uma dessas duas instruções, temos que usar o registrador ``Z`` para dizer onde queremos ler/gravar nosso dado. Então, dando um exemplo simples poderíamos pensar no seguinte código:

.. code-block:: asm
  
  main:
    
    ldi zl, low(data)
    ldi zh, high(data)
    lpm R0, Z

  data:
    .db 02, 03

Olhando esse exemplo poderíamos pensar que, ao fim da execução do código, o valor ``02`` estará gravado no registrador ``R0``, mas infelizmente não é tão simples assim. O problema é que a memóra flash é orientada a páginas e não a bytes e cada página possui dois bytes. Isso significa que em um atmega328p, por exemplo, que possui 32Kbytes de memória flash, temos na verdade 16K páginas que podem ser usadas com a instrução ``LPM``. Sabendo que cada página possui dois bytes, temos que ter uma forma de escolher qual desses dois bytes queremos ler/escrever.

Diferentes dos registradores de uso geral do AVR, que possuem 8 bits, o registrador ``Z`` possui 16 bits. Na verdade, o registrador ``Z`` é a junção dos registradores de 8 bits de uso geral: ``r31`` (``ZH``) e ``r30`` (``ZL``). A forma de escolher qual byte de uma página vamos ler/escrever é usando o bit menos significativo do registrador ``Z``.

O bit menos significativo com valor ``0`` indica que queremos mexer no primeiro byte da página e esse bit com valor ``1`` significa que queremos mexer no segundo byte da página. Os bits restantes (1 até 15) servem para indicar o endereço da página da memória flash que queremos mexer. Sabendo disso já podemos entender porque o exemplo de código acima não funciona.

No exemplo acima, o endereço da página (que tem como referência o label ``data:``) está ocupando o bit menos significativo. Isso aconteceu pois carregamos o endereço do label ``data:`` diretamente no registrador ``Z``. Vejamos um exemplo:

Se nosso label ``data:`` está posicionado no endereço ``0x6e9``, o exemplo acima deixou o registrador ``Z`` com o seguinte valor:

.. code-block:: text

        ZH        ZL
    00000110  11101001

E o que isso significa? Segundo o datasheet, significa que queremos ler o segundo byte da página (pois o bit menos signiicativo tem valor ``1``) e queremos esse byte da página com endereço ``000001101110100``, ou seja, ``0x374``. Isso definitivamente não é o que queríamos no início! Esse código de exemplo, está, na verdade, lendo a página de endereço ``0x374`` e não a página que queremos. Então como fazemos para ler a página correta? O que precisamos fazer é carregar o endereço de nossa página a partir do segundo bit menos significativo do registrador ``Z``, assim liberamos o primeiro bit para podermos indicar qual byte queremos ler. Existe uma forma muito simples de fazer isso: Basta multiplicar por ``2`` o endereço da página, antes de mover para o registrador ``Z``. Vejamos o mesmo exemplo acima, mas agora escrito da forma correta.


.. code-block:: asm
  
  main:
    
    ldi zl, low(data*2)
    ldi zh, high(data*2)
    lpm r0, Z

  data:
    .db 02, 03


Vamos considerar nossa label ``data:`` estando na mesma posição: ``0x6e9``. Quando rodamos esse código, o valor que é efetivamente carregado no registrador ``Z`` é ``0x6e9 * 2``, que é ``0xdd2`` e o registrador fica assim:

.. code-block:: text

        ZH        ZL
    00001101  11010010

Se fizermos a "decodificação" desse valor, segundo o que diz no datasheet, ou seja, pegando o bit menos significativo pra indicar o byte da página e o restante dos bits para indicar o endereço da página temos o seguinte: O bit menos significativo possui agora valor ``0``, o que significa que o primeiro byte da página será lido. E o restante dos bits (1 ao 15) possuem o segunte valor: ``000011011101001`` que é exatamente ``0x6e9``! Agora sim a leitura ficará correta e o código efetivamente gravará o valor ``02`` no registrador ``r0``.

E o que isso tudo tem a ver com nossa mistura de código C com código Assembly Legado? O problema é que esses endereços são calculados em tempo **de compilação**, ou seja, antes da fase de link-edição. Isso significa que quando o ``avr-gcc`` for juntar os dois códigos, todas as labels vão mudar de lugar (como já vimos nos posts anteriores) e isso significa que **todas** as leituras de dados da memória flash ficarão incorretas.

Nos posts anteriores, para resolver esse mesmo tipo de problema, ou seja, o deslocamento de código após a link-edição fizemos o parsing do dissasembly procurando por instruções de desvio (``jmp``, ``rjmp``, etc.), pegamos o endereço que essas instruções estavam referenciando, fizemos uma busca reversa em todos os labels encontrados no código original e adicionamos uma entrada na tabela de realocação. Isso era feito em conjunto pelas duas ferramentas que escrevi: ``extract-symbols-metadata`` [#]_ e ``elf-add-symbol`` [#]_.

Mas agora não podemos fazer isso pois uma operação de carga no registrador ``Z`` acaba se transformando em duas instruções no assembly final, dessa forma:

.. code-block:: asm

  ldi r30, 0xE6
  ldi r31, 0x0D

Seria insano procurar por esse "padrão" por todo o disassembly pra depois tentar de alguma forma "editar" a instrução no binário final. Por causa disso essa é a única "preparação" que você precisa fazer no seu código Assembly legado pra que seja possível juntá-lo com um código C moderno. Em todo o seu código original, quando você fizer uso da instrução ``LPM`` ou ``SPM`` você precisa levar em consideração o deslocamento que seu código Assembly vai sofrer após ser linkado com um código C. Uma forma simples de fazer isso é, por exemplo, sempre carregar valores no registrador ``Z`` usando uma macro, como essa:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0)
    ldi zh, high(@0)
  .endmacro


Depois que você já tiver modificado seu código original para fazer uso dessa macro, fica bem mais fácil corrigir os valores que são carregados no registrador ``Z``, pois poderemos mexer apenas nessa macro, e não no código inteiro. Esse é um exemplo de uso dessa macro:

.. code-block:: asm

  ldz data*2


O que precisamos agora é descobrir o quanto nosso código Assembly se deslocou depois que foi linkado ao código C. Devemos então adicionar esse "offset" ao código da nossa macro ``ldz``, assim todos os endereços serão corrigidos. Isso só funciona pois nosso código assembly original é composto por um grande arquivo binário. Se tivéssemos múltiplos arquivos Assembly, convertidos para ``avr-elf32`` e depois entregues para o ``avr-gcc`` para link-edição, provavelmente teríamos deslocamentos diferentes para as labels do código original. Por isso é importante manter seu código Assembly Legado como um binário único, convertido de Intel Hex para ``avr-elf32`` e entregue ao ``avr-gcc``.


Preparando a macro ldz para considerar o deslocamento aplicado pelo avr-gcc
===========================================================================


Como sabemos que todas as nossas labels serão deslocadas após o processo de link-edição, precisamos preparar nossa macro ldz para considerar esse offset e poder corrigir todos os endereços carregados no registrador ``Z``. Vejamos um exemplo simples:

Vamos considerar nossa label de exemplo ``data:``, localizada no endereço ``0x6e9``. Se formos rodar o código Assembly sozinho, a chamada à macro ``ldz`` ficaria assim (vamos substituir o nome da label pelo seu endereço para ficar mais claro):

.. code-block:: asm

 ldz 0x6e9*2

Se considerarmos um deslocamento de ``0x80`` após uma link-edição com um código C, nossa chamada à macro deveria ficar assim:

.. code-block:: asm

 ldz 0x769*2

isso porque ``0x6e9 + 0x80 = 0x769``. Isso significa que podemos reescrever nossa macro dessa forma:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0 + offset)
    ldi zh, high(@0 + offset)
  .endmacro

`(Nota importante: Entenderemos mais adiante porque não precisamos adicionar offset*2, já que o valor @0 já chega dentro da macro multiplicado)`.


Podemos definir a constante ``offset`` no início do nosso código Assembly, dessa forma:

.. code-block:: asm

 .equ offset = 0x80


A única forma que encontrei de descobrir esse deslocamento foi compilar o código inteiro e depois olhar no disassembly onde o código Assembly legado acabou sendo posicionado no binário final. Isso é chato (apesar de ser possível de automatizar) e passível de erro mas foi o que consegui fazer. Depois de descobrir o deslocamento, volto no código Assembly e adiciono esse offset ao código da macro ``ldz``.
    

O jeito simples de conferir se o offset escolhido está correto
==============================================================


Podemos colocar um código simples bem no início do nosso código assembly para nos ajudar a conferir se o ``offset`` escolhido está correto.

.. code-block:: asm

  _offset_check:
    ldz _data
  _offset_check_data:
    .db 01, 02

O que esse código faz é apenas carregar o endereço de uma label no registrador ``Z``. Ninguém vai chamar esse código, mas ele estará bem no início do nosso código Assembly e por isso aparecerá também no início do disasembly do binário final e poderemos conferir se as duas instruções ``ldi`` estarão carregando o endereço correto nos regisradores ``r31:r30`` (``Z``).

Vejamos como essa checagem funciona. Vamos link-editar um código assembly com essa checagem com um código C qualquer e vamos ver como fica o disassembly.


Esse será nosso código C:

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


Desse código, temos a função ``hello_main``, que estará implementada em Assembly.

Esse será nosso código Assembly:

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


Perceba que o valor da constante ``offset`` ainda está com valor ``0x00``, pois não sabemos onde nosso código Assembly será posicionado no binário final. Vejamos como fica o disassebly de uma primeira compilação:

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

O que temos que notar nesse disassembly é o ponto em que nosso código Assembly foi posicionado. Podemos ver que ele foi posicionado logo após a função ``f()`` (escrita em C). Nosso código Assembly começa no endereço ``0x008a``. Podemos observar também que o ``offset`` atual, com valor ``0`` está incorreto. Vejamos porque.

.. code-block:: objdump


  0000008a <_offset_check>:
    8a:	e4 e0       	ldi	r30, 0x04	; 4
    8c:	f0 e0       	ldi	r31, 0x00	; 0

  0000008e <_offset_data>:
    8e:	01 02       	muls	r16, r17

Aqui podemos ver que as duas instruções ``ldi``, que são responsáveis por carregar o endereço da label ``_offset_data`` no registrador ``Z`` (``r31:r30``), estão passando um endereço incorreto. Nossa label está localizada no endereço ``0x008e``, mas o que está sendo carregado nos registradores ``r31:r30`` é ``0x0004``, o que está claramente errado.

Agora vejamos como fica o disassembly quando adicionamos o offset correto, nesse caso ``0x008a``, que é exatamente o ponto onde nosso código Assembly foi posicionado no binário final.

Como não adicionamos nenhum código C novo, vamos olhar apenas para a parte do disassembly que realmente mudou.

.. code-block:: objdump

  0000008a <_offset_check>:
    8a:	ee e8       	ldi	r30, 0x8E	; 142
    8c:	f0 e0       	ldi	r31, 0x00	; 0

  0000008e <_offset_data>:
    8e:	01 02       	muls	r16, r17


Olhando agora para as instruções ``ldi`` vemos que ela carrega o endereço correto, que é ``0x008e``. Esse é exatamente o endereço na nossa label ``_offset_data``. Note que os valores já estão multiplicados por 2, isso porque estamos analisando o disassembly já do arquivo ``avr-elf32`` onde os novos endereços são o dobro dos endereços originais, que encontramos no arquivo ``.map`` produzido pelo ``avrasm2``. É por isso que não precisamos adicionar o valor de ``offset*2``, pois o offset que vemos no disassembly, nesse caso ``0x008a``, já está multiplicado.

Com esse ajuste de offset, seu código assembly consegue rodar junto com o código C e ainda fazer uso livre da memória flash para ler/gravar dados.


Bônus
=====

Agora que já podemos chamar código das duas linguagens e usar a memória flash livremente para ler/gravar dados seria interssante poder declarar novas constantes no código C e poder passá-las para o código Assembly. Pensando em uma possível migração de Assembly para C, é importante poder ir transferindo aos poucos, e isso inclui definições de constantes. Abaixo veremos como fazer as duas coisas: Declarar no C um valor que é salvo na memória flash e passá-lo para o código Assembly como parâmetro de função e declarar no Assembly um valor que é salvo na memória flash e passá-lo para o código C.


Declarando o valor no C e passando para o assembly
==================================================

Esse será nosso código C onde declaramos uma string que será salva na memória flash.

.. code-block:: c

  #include <avr/io.h>

  const char p[] PROGMEM = {"Hello from C."};

  extern void hello_main(const char []);

  void main(){
    hello_main(p);
  }


Quando fazemos a chamada à rotina Assembly ``hello_main()``, o endereço de ``p`` é passado nos registradores ``r25:r24``. vejamos o disassembly:

.. code-block:: objdump

  00000dce <main>:
   dce:   8c e7           ldi     r24, 0x7C       ; 124
   dd0:   90 e0           ldi     r25, 0x00       ; 0
   dd2:   0e 94 a2 06     call    0xd44   ; 0xd44 <hello_main>
   ddc:   08 95           ret


Vemos nesse caso que o valor que é passado é ``0x007c``. A boa notícia é que esse valor já está pronto para ser usado com a instrução ``LPM``, ou seja, já está multiplicado por 2. No código Assembly basta mover esse valor para o registrador ``Z`` e usar normalmente. Vejamos o código Assembly que receberá esse valor:

.. code-block:: asm

  hello_main:
    mov zl, r24
    mov zh, r25
    lpm r0, Z    

Definindo o valor no Assembly e passando para o C
=================================================

Agora faremos o mesmo, mas tendo definido a constante no Assembly. Vejamos o código C que receberá o endereço da memória flash onde o dado estára gravado.

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

Nesse código chamamos a rotina ``hello_main``, que está escrita em Assembly. Essa rotina chama de volta o código C através da função ``c_read_flashbyte()``, dessa vez passando como parametro o endereço onde o dado está gravado. Fazemos então a leitura desse dado com a função ``pgm_read_byte_near()`` e retornamos o valor lido para o Assembly. Vejamos o código assembly:

.. code-block:: asm
  
  hello_main:

    ldi r25, high(flash_byte_from_asm*2 + offset)
    ldi r24, low(flash_byte_from_asm*2 + offset)
    call c_read_flashbyte
    
  flash_byte_from_asm:  .db "X", 0

Vejamos como fica o disassembly disso tudo:

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


Passamos o endereço pelos registradores ``r25:r24``. Note que estamos passando o endereço correto, ``0x0DF0``. A função ``c_read_flashbyte`` move o conteúdo dos registradores ``r25:r24`` para o registrador ``Z`` (``r31:r30``) e faz a leitura do dado com a instrução ``LPM``, guardando o resultado em ``r24``. E esse é exatamenteo o registrador onde estará, nesse caso, o valor ``'X'``.

Então para passarmos endereços da memória flash declarados no Assembly precisamos sempre considerar o offset que esse código sofreu quando foi posicionado no binário final.


.. [#] `Static random-access memory <https://en.wikipedia.org/wiki/Static_random-access_memory>`_
.. [#] `EEPROM <https://en.wikipedia.org/wiki/EEPROM>`_
.. [#] `extract-symbols-metadata <{filename}/extra/extract-symbols-metadata-v2.py>`_
.. [#] `elf-add-symbol <{filename}/extra/elf-add-symbol-v2.cpp>`_
