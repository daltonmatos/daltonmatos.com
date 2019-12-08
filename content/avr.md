---
title: "Misturando código do avrasm2 com código do avr-gcc: Uma prova de conceito"
author: Dalton Barreto
type: "about"
---

Abaixo você encontra uma pesquisa que fiz onde mostro, na prática, como mesclar código de um projeto puramente Assembly (feito com `avrasm2` e que gera apenas um arquivo [Intel Hex](https://en.wikipedia.org/wiki/Intel_HEX)) com um projeto Moderno C (feito com `avr-gcc`) que pode fazer uso de conceitos mais avançados como [realocação de código](https://en.wikipedia.org/wiki/Relocation_\(computing\)), [tabela de símbolos](https://en.wikipedia.org/wiki/Symbol_table), [link-edição](https://en.wikipedia.org/wiki/Linker_\(computing\)) e outros.

A pesquisa é dividia em 4 posts, onde avanço gradualmente resolvendo os problemas que encontrei pelo caminho. Todos os códigos mostrados nos posts foram testados na prática e são funcionais. Os testes foram feitos em um Arduino Nano (ATMega328p) e em uma [placa controladora de quadcópteros KK2](https://hobbyking.com/pt_pt/hobbyking-kk2-1-5-multi-rotor-lcd-flight-control-board-with-6050mpu-and-atmel-644pa.html) (ATMega644p). A placa que usei está atualmente descontinuada, a versão seguinte [está aqui](https://hobbyking.com/pt_pt/hobbykingtm-kk2-1hc-multi-rotor-hard-case-flight-control-board.html).

Abaixo estão os links e uma breve explicação dos quatro posts:


1. [Chamando código Assembly legado (AVRASM2) a partir de um código novo em C (avr-gcc)]({{<ref "/posts/chamando-codigo-assembly-legado-avrasm2-a-partir-de-um-codigo-novo-em-c-avr-gcc.md">}})


O primeiro mostra que é possível chamar código assembly apenas alterando o endereço de símbolos no arquivo elf gerado pelo `avr-gcc` (a partir de um `main.c`). A abordagem desse post deixa de funcionar assim que começamos a escrever códigos Assembly mais complexos, por exemplo, contendo instruções de desvio (`jmp`, `rjmp`, `call`, etc).

2. [Convertendo Intel HEX para ELF32-avr criando tabela de símbolos e tabela de realocação]({{< ref "/posts/convertendo-ihex-para-elf-preservando-as-labels-originais-como-simbolos.md">}})

O segundo resolve o problema do post anterior, em relação ao uso de instruções de desvio no código assembly. Nesse post manipulamos a tabela de realocação do elf que geramos a partir do nosso código assembly, fazendo assim com que o ``avr-gcc`` altere os endereços das instruções de desvio, gerando um binário final correto.

3. [Chamando código novo C (avr-gcc) a partir de código legado Assembly (avrasm2)]({{<ref "/posts/chamando-codigo-novo-em-c-avr-gcc-a-partir-de-um-codigo-assembly-legado-avrasm2.md">}})

O terceiro evolui a técnica usada no post anterior. Nesse post adicionamos o conceito de símbolo externo (já tínhamos usado símbolos internos antes). Desta forma podemos adicionar um símbolo externo ao elf gerado a apartir do código Assembly, podendo assim declarar rotinas no Assembly que terão suas implementações substituídas, durante a link-edição, por implementações em C.

4. [Lidando com dados gravados na memória flash, EEPROM e SRAM]({{<ref "/posts/lidando-com-dados-inicializados-gravados-na-memoria-flash-eeprom-sram.md">}})

O quarto e último post lida com constantes que são salvas na memória de código do chip. Lidamos específicamente com as instruções ``LPM`` e ``SPM``, que nos chips AVR trabalham de uma forma peculiar e por isso demandam ajuste de endereços ainda durante a compilação.


## Códigos usados durante a pesquisa

Abaixo você encontra o link do repositório onde existem os códigos que foram usados durante essa pesquisa. São códigos que fiz como prova de conceito para validar as hipóteses criadas durante a pesquisa, portando não espere encontrar nada bonito. =D

 * https://github.com/daltonmatos/avrgcc-mixed-with-avrasm2
