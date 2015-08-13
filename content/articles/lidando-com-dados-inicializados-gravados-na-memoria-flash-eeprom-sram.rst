:title: Lidando com dados gravados na memória flash, EEPROM e SRAM
:date: 2015-08-12
:status: draft
:author: Dalton Barreto
:slug: lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram


Esse post faz parte de uma `série de posts <{filename}chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_ sobre mistura de código C (avr-gcc) com código Assembly (``avrasm2``). Se você ainda não leu os posts anteriores, recomendo que leia antes de prosseguir.


Contexto
========

Até agora, nos posts anteriores vimos apenas como fazer chamdas de função de uma linguagem para outra, mas uma parte muito importante de qualquer projeto com micro-controladores é a possibilidade de gravar dados na area de memória de código (memória flash). É bem comum usar essa memória para gravar valoresque serão usados pelo código. O mais comum é vermos strings sendo guardadas para uso futuro, mas é perfeitamente possível guardarmos outros valores como constantes, números e até mesmo definição de fontes, para o caso de estarmos lidando com displays de LCD.

Além da memória flash, temos duas outras memórias dispońiveis parausar dessa mesma forma. Amemória SRAM [#]_ e a EEPROM [#]_. Vamos logo abaixo como gravamos/lemos dados dessas três memórias disponíveis nos micro-controladores AVR (pelo menos na maioria deles).


Lendo/Gravando dados na memória SRAM e EEPROM
=============================================

Tanto a memória SRAM quanto a EEPROM possuem posicionamentos fixosem cada chip AVR, isso significa que, independente da lingagem que você escrever o código que ira ler/escrever nessas memórias, o endereço de leitura/escrita será sempre o mesmo. Isso significa que não precisamos nos preocupar com nenhum tipo de deslocamento de código quando fizermos a link-edição com algum código C. Tanto o ``avr-gcc`` quanto o ``avrasm2`` vão inicializar corretamente os valores dos endereços dessas duas memórias e o código poderá referenciar esses endereços livremente.


Lendo/Gravando dados na memória Flash
=====================================

O problema começa quando precisamos ler/gravar dados na memória flash. Isso acontece pois as duas instruçoes que devemos usar para isso, `LPM` e `SPM` trabalham de uma forma peculiar, que explico a seguir:

Quando usamos quaisquer uma dessas duas instruçoes, temos que usar o registrador `Z` para dizer onde queremos ler/gravar nosso dado. Então pensando em um exemplo simples de uso poderíamos pensar no seguinte exemplo de código:

.. code-block:: asm
  
  main:
    
    ldi zl, low(data)
    ldi zh, high(data)
    lpm R0, Z

  data:
    .db 02, 03



Olhando esse exemplo podeíamos pensar que, ao fim da execução desse código, o valor ``02`` estará gravado no registrador ``R0``, mas infelizmente não é tão simples assim. O problema é que a memóra flash é orientada a páginas e não a bytes e cada página possui dois bytes. Isso significa que em um atmega328p, por exemplo, que possui 32Kbytes de memória flash, temos na verdade 16K páginas que podem ser usadas com a instrução ``LPM``. Sabendo que cada página possui dois bytes, temos que ter uma forma de escolher qual desses dois bytes queremos ler/escrever.

Diferentes dos registradores de uso geral do AVR, que possuem 8 bits, o registrados ``Z`` possui 16 bits. Na verdade, o registrador ``Z`` é a junção dos registradores ``r31`` (``ZH``) e ``r30`` (``ZL``). A forma de escolher qual byte de uma página vamos ler/escrever é usando o bit menos significativo do registrador ``Z``.

O bit menos significativo com valor ``0`` indica que queremos mexer no primeiro byte da página e esse bit com valor ``1`` significa que queremos mexer no segundo byte da página. Os bits restantes (1 até 15) servem para indicar o endereço da página da memória flash que queremos mexer. Isso que descobrimos até agora já é suficiente para entendermos porque o exemplo de código acima não funciona.

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


Vamos conseiderar nossa label ``data:`` estando na mesma posição: ``0x6e9``. Quando rodamos esse código, o valor que é efetivamente carregado no registrador ``Z`` é ``0x6e9 * 2``, que é ``0xdd2`` e o registrador fica assim:

.. code-block:: text

        ZH        ZL
    00001101  11010010

Se fizermos a "decodificação" desse valor, segundo o que diz no datasheet, ou seja, pegando o bit menos significativo pra indicat o byte da página e o restante dos bits para indicar o endereço da página temos o seguinte: O bit menos significativo possui agora valor ``0``, o que significa que o primeiro byte da página será lido. E o restante dos bits (1 ao 15) possuem o segunte valor: ``000011011101001`` que é exatamente ``0x6e9``! Agora sim a leitura ficará corretae o código efetivamente gravará o valor ``02`` no registrador ``r0``.

E o que isso tudo tem a ver com nossa mistura de código C com código Assembly Legado? O problema é que esses endereços são calculados em tempos **de compilação**, ou seja, ates da fase de link-edição. Isso significa que quando o ``avr-gcc`` for juntaros dois códigos, todas as labels vão mudar de lugar (como já vimos nos posts anteriores) e isso significa que **todas** as leituras de dados da memória flash ficarão incorretas.

Nos posts anteriores, para resolver esse mesmo tipo de problems, ou seja, deslocamento de código após a link-edição fizemos o parsing do dissasembly procurado por instruçoes de desvio (``jmp``, ``rjmp``, etc.), pegávamos o endereço que essas instruçoes estavam referenciando, faziamos uma busca reversa em todos os labels encontrados no código original e adicionávamos uma entrada na tabela de realocação. Isso era feito, em conjunto, pelas duas ferramentas que escrevi: ``extract-symbols-metadata`` [#]_ e ``elf-add-symbol`` [#]_.

Mas agora não podemos fazer isso pois uma operação de carga no registrador ``Z`` acaba se ransformando em duas instruçoes no assembly final, dessa forma:

.. code-block:: asm

  ldi r30, 0xE6
  ldi r31, 0x0D

Seria insano procurar por esse "padrão" por todo o disassembly pra depois tentar de alguma forma "editar" a instrução no binário final. Por causa disso essa é a única "preparação" que você precisa fazer no seu código Assembly legado pra que seja possível juntá-lo com um código C moderno. Em todo o seu código original, quando você fizer uso da instrução ``LPM`` ou ``SPM`` você precisa levar em consideração o deslocamento que seu código Assembly vai sofrer após ser linkado com um código C. Uma forma simples de fazer isso é, por exemplo, sempre carregar valores no registrador ``Z`` usando uma macro, como essa:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0)
    ldi zh, high(@0)
  .endmacro


Depois que você já tiver modificado seu código original para sempre fazer uso dessa macro, fica bem mais fácil corrigir os valores que são carregados no registrador ``Z``, pois poderemos mexer apenas nessa macro, e não no código inteiro. Esse é um exemplo de uso dessa macro:

.. code-block:: asm

  ldz data*2


O que precisamos agora é descobrir o quanto nosso código Assembly se deslocou depois que foi linkado ao código C. Devemos então adicionr esse "offset" ao código da nossa macro ``ldz``, assim todos os endereços serão corrigidos. Isso só funciona pois nosso código assembly original é composto por um grande arquivo binário. Se tivéssemos múltiplos arquivos Assembly, convertidos para ``avr-elf32`` e depois entregues para o ``avr-gcc`` para link-edição, provavelmente teríamos deslocamentos diferentes para as labels do código original. Por isso é importante manter seu código Assebly Legado como um binário único, convertido de Intel Hex para ``avr-elf32`` e entregue ao ``avr-gcc``.


Preparando a macro ldz para considerar o deslocamento aplicado pelo avr-gcc
===========================================================================


Como sabemos que todas as nossas labels serão deslocadas após o processo de link-edição, precisamos preparar nossa macro ldz para considerar esse offset e poder corrigir todos os endereços carregados no registrador ``Z``. Vejamos um exemplo simples:

Vamos considerar nossa label de exemplo ``data:``, localizada no endereço ``0x6e9``. Se formos rodar o código Assembly sozinho, a chama à macro ``ldz`` ficaria assim (vamos substituir o nome da label pelo seu endereço para ficar mais claro):

.. code-block:: asm

 ldz 0x6e9*2

Se considerarmos um deslocamento de ``0x80`` após uma link-edição com um código C, nossa chamada à macro deveria ficar assim:

.. code-block:: asm

 ldz 0x769*2

isso porque ``0x6e9 + 0x80 = 0x769``. Mas lembre-se o offset só é adicionado dentro da macro ``ldz``, o que significa que o endereço original **já estará multiplicado por 2**. Mas podemos usar um pouco de matemática básica para conseguir adicionar o offset mesmo tendo o endereço original já multiplicado por 2. Vejamos:

.. code-block:: test

  (0x6e9 + 0x80) * 2 é o mesmo que (0x6e9 * 2) + (0x80 * 2)

Isso sifnifica que podemos re-escrever nossa macro dessa forma:

.. code-block:: asm

  .macro ldz
    ldi zl, low(@0 + (offset * 2))
    ldi zh, high(@0 + (offset * 2))
  .endmacro
 
Podemos definir a constante ``offset`` no início do nosso código Assembly, dessa forma:

.. code-block:: asm

 .equ offset = 0x80


Econtrando o deslocamento aplicado pelo avr-gcc
===============================================

A única forma que encontrei de descobrir esse deslocamento foi compilar o código inteiro e depois olhar no disassembly onde o código Assembly legado acabou sendo posicionado no binŕio final. Isso é chato (apesar de ser possível de automatizar) e passível  de erro mas o que consegui fazer. Depois de descobrir o deslocamento, volto no código Assembly e adiciono esse offset ao código da macro ``ldz``.
    

Confirmar que, quando o valor de ``offset/2`` for ímpar, devemos somar ``1``, pois assim não mexemos no bit menos significativo do registrador ``Z``. Se mexermos nesse bit, estamos alterando qual byte da página está sendo lido/escrito.


O jeito simples de conferir se o offset escolhido está correto
==============================================================


Podemos colocar um código simples em no início do nosso código assembly para nos ajudar a conferir seo ``offset`` escolhido está correto.

.. code-block:: asm

  check:
    lzd _data
  data:
    .db 01, 02

O que esse código faz é apenas carregar o endereço de uma label no registrador ``Z``. Ninguém vai chamar esse código, mas ele estará bem no início do nosso código Assembly e por isso aparecerá também no início do disasembly do binário final e poderemos conferir se as duas instruçoes ``ldi`` estão carregando o endereço correto nos regisradores ``r31:r30`` (``Z``).

Mosrar exemplo de disassembly e lembrar que o elf o endereço é o dobro do IHEX, por isso as instrucoes ``ldi`` já trazem o valor correto do label. 

Notes
=====

Algumas ideias para se passar dados da memória flash do C pra asm e do asm pra C.


C => ASM
========

.. code-block:: c

  char* a PROGMEM = "abc";



call_asm_routine(a);

No assembly:

; recebe o parametroem r25:r24 ? Se sim:
mov r26, 25
mov r27, r24
movw z, x ; x é r25:r24

;conferir se o C já passa o valor multiplicado por 2 !! Senão, multiplicar.
shift z, 1

call PrintString

Deve dar para acessar um .db definido no assembly dessa forma:

.. code-block:: c

  extern char* a;


pgm_read_byte(a);

e no assembly:

a:
  .db 10, 20


Tentar compilar o código oficial e juntar com C - Validar
=========================================================

No exemplo do hello-world-st7565 quando incluo mais de uma definição de fonte (ou até apenas uma que não seja a f6x8), dá um erro de "out of range error" no momento de adicionar alguns simbolos na symbol table do elf gerado a partir do assembly. Tentar entender isso e resolver.

Fazer um Teste rapido. Ver se o código original roda sem nenhum interupt registrado, apenas o de reset. Se rodar, dápra validar isso aqui apenas com um main() simples no C que chama o reset: do assembly. Funcina apenas com o reset e o IsrPwmEnd. Verificar porque sem esse ultimo interrupt handler o display nem exibe nada.


Usar ldz em todo o codigo - Validar em Voo
==========================================

Todas as instrucoes que usam "ldi zl" seguido de "ldi zh" devem ser convertidos para "ldz <param>".

A principio, chamadas como "ldi zl, <N>", não precisam, pois parece que o código está usando o Z apenas como contador e não como preparação para chamar a instrução "lpm".

Fazer teste de voo com essa modificação já feita!

Lembrar de mudar o simbolo TabCh. Todas as fontes devem estar com "+ (offset * 2)". Mas já terei descoberto isso se estiver fazendo o teste de voo, já que a placa não exibirá nada no display se isso não estiver correto. =D

Cuidado com "ldz 0" . O código do novo ldz deve fazer um "if" para quando o valor recebido é "0". Se não fizer vai distorcer o valor final, já que 0 * 2 é diferente de (0 * 2) + (offset * 2), já que offset é sempre > 0.


.. [#] `Static random-access memory <https://en.wikipedia.org/wiki/Static_random-access_memory>`_
.. [#] `EEPROM <https://en.wikipedia.org/wiki/EEPROM>`_
.. [#] `extract-symbols-metadata <{filename}/extra/extract-symbols-metadata-v2.py>`_
.. [#] `elf-add-symbol <{filename}/extra/elf-add-symbol-v2.cpp>`_
