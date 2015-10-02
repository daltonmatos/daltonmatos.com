:title: Misturando código do avrasm2 com código do avr-gcc: Uma prova de conceito.
:author: Dalton Barreto
:lang: pt
:translation: false
:slug: avrgcc-avrasm2

Abaixo você encontra uma pesquisa que fiz onde mostro, na prática, como mesclar código de um projeto puramente Assembly (feito com avrasm2 e que gera apenas um arquivo Inter Hex) com um projeto Moderno C (feito com avr-gcc) que pode fazer uso de conceitos mais avançados como realocação de código, tabela de símbolos, link-edição e outros.

A pesquisa é dividia em 4 posts, onde avanço gradualmente resolvendo os problemas que encontrei pelo caminho. Todos os códigos mostrados nos posts foram testados na prática e são funcionais. Os testes foram feitos em um Arduino Nano (ATMega328p) e em uma `placa controladora de quadcópteros KK2 <http://www.hobbyking.com/hobbyking/store/__54299__Hobbyking_KK2_1_5_Multi_rotor_LCD_Flight_Control_Board_With_6050MPU_And_Atmel_644PA.html>`_ (ATMega644p).

Abaixo está o link e uma breve explicação dos os quatro posts:


1. `Chamando código Assembly legado (AVRASM2) a partir de um código novo em C (avr-gcc) <{filename}/articles/chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.rst>`_

O primeiro ...

2. `Convertendo Intel HEX para ELF32-avr criando tabela de símbolos e tabela de realocação <{filename}/articles/convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.rst>`_

O segundo ...

3. `Chamando código novo C (avr-gcc) a partir de código legado Assembly (avrasm2) <{filename}/articles/chamando-codigo-novo-em-c-avr-gcc-a-partir-de-um-codigo-assembly-legado-avrasm2.rst>`_

O terceiro ...

4. `Lidando com dados gravados na memória flash, EEPROM e SRAM <{filename}/articles/lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram.rst>`_

O quarto e último ...
