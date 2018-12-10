---
title: Usando vim como interpretador de código
date: 2018-11-25
author: Dalton Barreto
tags: [vim, script, code, programming, vimscript, vimL]
---

Pra quem traballha com programação, escrever código pode representar grande parte das atividades do dia-a-dia.
À medida que o tempo vai passando vamos escrevendo código e nem mais percebendo o que é necessário para rodar esss códigos.

Mas quando paramos para pensar nisso, independente da linguagem que usamos, tudo acontece meio que da mesma forma: O código que escrevemos
deve ser interpretado por "alguém", seja esse "alguém" um outro código (um interpretador, por exemplo) ou um hardware (um processador, por exemplo).

O [Vim](https://www.vim.org) é um editor de texto **extremamente** extensível e isso acontece pois a forma de extendê-lo é através de uma [linguagem de programação](https://pt.wikipedia.org/wiki/Linguagem_de_programa%C3%A7%C3%A3o). Isso praticamente não te impõe limites no que é possível fazer.

A linguagem criada para extender o vim é chamada de vimscript ou vimL. É uma lingugem de programação como qualquer outra. Possui, dentre outras características:

* Variáveis (locais, globais, somente-leitura, etc);
* Condicionais (`if, else, elseif`);
* Operações lógicas (`>, <, >=, <=, ==`, etc);
* Expressoes matemáticas (`+`, `-`, `*`, `/`);
* Expressões booleanas (`(a + 30) > 5`, etc);
* Expressões bitwise (`and(), or(), xor()`);
* Funções (inclusive com númemro variável de parametros) e Ponteiros para funções (`FuncRef`);
* Variáveis complexas: (`List`, `Dict`);
* Comunicação assíncrona com outros processos (`Channels`);
* Genrenciamento de sub-processos (`job`);
* Exceptions (`try/catch/endtry`);
* Funções built-in.

Alguns exemplos de funcções built-in:

* Manupilação de strings (`tolower(), toupper(), stridx()`);
* Manipulação de Listas (`len(), get(), empty(), insert(), add(), split()`);
* Manipulação de Dicionários (`get(), len(), has_key(), filter(), items()`);
* Input/Output (`input(), getchar(), confirm()`), passagem de parametros na linha de comando (`argc(), argv()`);
* Assert funcions (`assert_true(), assert_equal(), assert_exception()`);

Na massiva maioria das vezes (todas?) onde vemos `vimL` o código está sendo aplicado para extender o próprio vim, geralmente em forma de um plugin. Mas `vimL` é uma linguagem bastante completa e podemos escrever scripts genéricos, para uso geral assim como escrevemos bash ou python.

E é aqui que começa esse post. Vamos escrever um script simples e executá-lo como se fosse um script shell, mas o código estará escrito em `vimL`.

# Anatomia de um script

Um script é composto geralmente apenas por código. E para rodá-lo precisamos de um interpretador que entenda esse código. Um exemplo simples de um script shell:

```
echo "Hello World"
```

E podemos rodar com **qualquer** shell que endenda esse código (pode ser `bash`, `zsh`, etc):

```
$ bash meu-script.sh
Hello World
```

## Indicando o interpretador no código do próprio script

Existe uma forma de já pré-escolher qual será o interpretador usado para rodar nosso script. Essa forma é usando o que chamamos de [shebang](https://en.wikipedia.org/wiki/Shebang_(Unix)). O que fazemos é adicionar um comentário funcional na primeira linha do nosso script, assim:

```
#!/bin/bash
echo "Hello World"
```

A partir de agora podemos chamar nosso script apenas pelo nome, assim:

```
./meu-script.sh
Hello World
```


O que pouca gente sabe é que nessa linha podemos colocar o caminho de **qualquer** programa, inclusive de outro script. Porque não colocar ali uma chamada ao próprio vim?

É isso que vamos fazer!


# Usando vim para rodar um script vimL


Vamos usar o seguinte script como prova de conceito:

```
echo "Hello World"
```

Gravamos esse código em `meu-script.vim`.

Olhando o exemplo acima (do shell script), pensamos automaticamente em fazer apenas:

```
$ vim meu-script.vim
```

O problema começa pois como o vim é originalmente um editor de texto, essa linha que chamamos vai na verdade abrir o vim e nos mostrar o **conteúdo** do nosso script, que é exatamente o que fazemos quando estamos usando o `vim` no dia-a-dia. Então como dizer ao `vim` que queremos, na verdade, **executar** o script?

O vim possui um flag, `--cmd` que permite que ele execute um comando qualquer. Então nossa primeira tentativa pode ser:

```
$ vim --cmd "source ./hello-world.vim"
Hello World
Press ENTER or type command to continue
```

De fato **FUNCIONA**, mas apenas parcialmente. Isso pois o `vim` executa nosso comando mas depois continua seu caminho normal, que é ser um editor de texto. Então aqui, depois de pertar `ENTER` acabamos com o vim aberto e não é o que queremos, já que queremos voltar ao terminal depois que nosso script terminar de rodar.

Podemos então adicionar `:qall!` no final do nosso script, isso vai fazer com que o `vim` feche automaticamente.

Nosso novo script fica assim:

```
echo "Hello World"
:qall!
```

E podemos rodar assim:

```
$ vim --cmd "source ./hello-world.vim"
Hello World
```

Nesse momento temos nosso primeiro script em `vimL` podendo ser rodado na linha de comando.


## Rodando uma instância de vim sem nenhuma configuração personalizada

Apesar de termos conseguido rodar nosso script, temos ainda um problema. Essa instância de `vim` que estamos usando para interpretar nosso script está carregando configurações customizadas escolhidas pelo usuário. Isso pode ser muito ruim pois não temos controle sobre quais são essas configurações e elas podem influenciar na execução do nosso script.

Para rodar um `vim` sem nenhuma configuração, podemos usar a opção `-u <file>` que diz ao `vim` para usar o arquivo `<file>` como sendo o `.vimrc`. Assim nós conseguimos substituir toda e qualquer configuração feita pelo usuário.

Então nosso script pode ser rodado assim:

```
$ vim -u hello-world.vim
Hello World
```

## Usando vim no shebang do nosso script

Uma forma de podermos chamar nosso script diretamente é colocar o `vim` no `shebang` do nosso script, assim:

```
#! vim -u
echo "Hello World"
:qall!
```

e a partir de agora podemos rodar nosso script diretamente:

```
$ ./hello-world.vim
Hello World
```

# Exemplo de script um pouco mais complexo e novos problems que isso traz

Vamos escrever um script um pouco mais complexo. Vamos retornar a soma de todos os parametros passados na linha de comando.

Esse é o código:

{{<highlight viml>}}
#! vim -u

let s:sum = 0

for n in argv()
 let s:sum += n
endfor

echo s:sum

:qall!
{{</highlight>}}

Colocamos em `soma.vim`. E rodamos com:


```
$ ./soma.vim 10 20 30 40                        
4 files to edit
100
```

O `vim` sendo um editor de texto espera que seus argumentos sejam arquivos a serem editados e por isso coloca esse output junto com o output do nosso script:

```
4 files to edit
```

Infelizmente isso [não é configurável](https://superuser.com/questions/545047/how-do-i-supress-the-2-files-to-edit-message-in-vimdiff), ou seja, sempre que você passar mais de 1 argumento para o seu script, essa frase vai aparecer. Mas já já veremos uma forma de driblar isso.


## Quando o script está em uma linha de comando com pipe (|)

Um outro problema é quando rodamos nosso script em um linha de comando mais complexa, com pipe (`|`). Veja:

```
$ ./soma.vim 10 20 30 40 | cat                  
Vim: Warning: Output is not to a terminal
100
4 files to edit
```

Felizmente esse warning é configurável através da opção `--not-a-term`. Então basta adicionar essa opção em nosso `shebang`, certo? Na verdade não. Uma das regras é que o comando que está no `shebang` só pode receber **um** parametro. Veja o que acontece quando tentamos passar mais de um parametro:

```
#! vim --not-a-ter -u
echo "Hello World"
:qall!
```

Quando rodamos, vemos:

```
$ ./hello-world.vim
VIM - Vi IMproved 8.1 (2018 May 18, compiled Nov 11 2018 17:01:22)
Unknown option argument: "--not-a-ter -u"
More info with: "vim -h"
```

veja como o `vim` considera todos os parametros passados como sendo um só: `"--not-a-ter -u"`. Aqui coloquei de propósito um parametro errado pois caso contrário nenhum erro é mostrado e o `vim` apenas abre o arquivo que estamos tentando executar.


## Usando um segundo script como interpretador

Apesar do comando no `shebang` poder receber apenas um parametro é permitido colocar ali o caminho de um outro script. Então podemos fazer uma espécie de "wrapper" que vai montar a linha de comando de chamada do `vim` pra nós. Esse pode ser nosso wrapper:

```
#! /bin/bash

vim --not-a-term -u "$@" | sed '/files\ to\ edit$/d'
```

A partir de agora podemos usar esse script como sendo o "interpretador" do nosso script `vimL`. Mas ainda temos um problema, pois parece que tudo que o código `vimL` imprime vai para `stderr`. Então temos que adicionar `2>&1` em nosso runner, assim:

```
#! /bin/bash

vim --not-a-term -u "$@" 2>&1 | sed '/files\ to\ edit$/d'
```

Podemos então gravar esse código em `/usr/local/bin/viml` e usá-lo no `shebang` de qualquer script escrito em `vimL`.

{{<highlight viml>}}
#! /usr/bin/env viml

let s:sum = 0

echo 'Somando números: ' . join(argv(), ' + ')
for n in argv()
 let s:sum += n
endfor

echo 'Resultado: ' . s:sum

:qall!
{{</highlight>}}

Assim podemos rodar nosso script diretamente:

```
./run.vim 3 4 4 5 5 6                      
Somando números: 3 + 4 + 4 + 5 + 5 + 6
Resultado: 27
```

E podemos também usar nosso script em uma linha de comando com pipe:

```
./run.vim 3 4 4 5 5 6 | grep Res
Resultado: 27
```

E assim temos uma forma bem transparente para podermos escrever scripts de uso geral usando `vimL` como linguagem de programação e usando o próprio vim como interpretador desses scripts.


