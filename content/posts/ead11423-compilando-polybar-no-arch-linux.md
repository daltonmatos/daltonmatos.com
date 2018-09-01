---
title: Compilando polybar no Arch Linux
author: Dalton Barreto
tags: [tiling, i3, linux, statusbar, wm]
date: 2018-08-31
---

[Polybar](https://github.com/jaagr/polybar) é uma (de várias) possíveis implementações de statusbar para gerenciadores de janelas para o projeto [X.org](https://x.org) (ou apenas `X`, `xorg-server`, `Xorg`).

Window manager (ou apenas WM) é basicamente a parte responsável por "falar" com o `xorg-server` e desenhar as janelas dos programas que você abre. O WM faz também muitas outras coisas, mas para o que vamos ver aqui saber isso basta.

Todas as opções de interface gráfica que hoje existem para o Xorg possuem um Window Manager. Quando você pega um exemplo como o Gnome Shell, ele é considerado um "Desktop Environment" pois possui muito mais do que apenas o WM. Tem, por exemplo, File Manager, Painel de Controle completo com suporte a impressora, bluetooth, rede (wi-fi e cabeada), gerência de usuários, localização, configuração de teclado etc.

Quando você usa um WM puro, tudo isso some e você precisa fazer isso através de outros "helper programs".

# i3wm

O [i3wm](https://i3wm.org) (ou apenas `i3`) é um Window Manager minimalista. Diferente de outros projetos que também fornecem um Window Manager (como por exemplo Gnome e KDE) ele é um tipo de WM chamado de [tiling window manager](https://en.wikipedia.org/wiki/Tiling_window_manager).

Assim que conheci esse conceito o que mais se destacou pra mim foi o fato de um tiling window manager não ter o conceito de "Alt+Tab" que estamos tão acostumados a usar.

Sem essa possibilidade temos que ter outra forma de trocarmos foco de uma janela para outra e é exatamente aí que acho que o `i3` (e outros tiling WM) brilham: É possível operar essa interface gráfica usando apenas o teclado. Trocar o foco, redimensionar janelas, toogle fullscreen, fechar, mover, etc.

# O papel da statusbars em um WM

Um tiling WM funciona perfeitamente sem uma statusbar. Veja:

## i3 sem nenhuma statusbar

[![i3 sem statusbar](/static/ead11423/i3-with-no-status-bar.png)](/static/ead11423/i3-with-no-status-bar.png)

## i3 com statusbar padrão

[![i3 sem statusbar](/static/ead11423/i3-with-default-status-bar.png)](/static/ead11423/i3-with-default-status-bar.png)

## Então pra que serve uma statusbar?

A ideia é ela poder exibir informações adicionais, tais como: Indicação de volume, indicação de conectividade de rede (wi-fi e cabo), nível da bateria (com indicador de carregamento) e muitas outras coisas.

Cada uma dessas informações são chamadas de "módulos" ou "blocks". Cada módulo exibe uma informação e você pode colocar quantos você quiser (ou couber) na sua statusbar.

A maioria (todas?) as statusbars são implementadas basicamente da mesma forma, ou seja, os conteúdos que elas exibem são, na verdade, outputs de scripts que você escolhe/escreve.

Uma statusbar implementa apenas a possibilidade de exibir informações adicionais, ou seja, você tem que escrever **todos** os scripts que vai fornecer as informações que serão exibidas.

É nesse ponto que projetos como o da [Polybar](https://github.com/jaagr/polybar) se tornam interessantes, pois já trazem módulos pré-implementados e que estão preparados para exibir uma série de informações na statusbar.

Isso é ótimo pois já te dá a oportunidade de ter uma statusbar com informações úteis sem ter que implementar cada script individualmente.

# Polybar no Arch Linux

A [Polybar](https://github.com/jaagr/polybar) é escrita em C++ e já vem com muitos plugins. Alguns exemplos: battery, cpu, date, memory, xwindow, etc.

A lista completa está na [Wiki do projeto](https://github.com/jaagr/polybar/wiki).

Apesar da documentação apontar um [PKGBUILD](https://aur.archlinux.org/packages/polybar/) para compilar/instalar a Polybar no Arch, ele não funciona.

Usando um [AUR](https://wiki.archlinux.org/index.php/Arch_User_Repository) helper qualquer, nesse caso o [yay](https://github.com/Jguer/yay) obtemos um erro ao tentar instalar a `polybar`.

```
$ yay -S ploybar
...
...
-- Found PythonInterp: /home/daltonmatos/.pyenv/shims/python2.7 (found suitable version "2.7.15", minimum required is "2.7") 
-- XCB[XCB]: Found component XCB
-- Found XCB_XCB: /usr/lib/libxcb.so  
-- XCB[ICCCM]: Found component ICCCM
-- Found XCB_ICCCM: /usr/lib/libxcb-icccm.so  
-- XCB[EWMH]: Found component EWMH
-- Found XCB_EWMH: /usr/lib/libxcb-ewmh.so  
-- XCB[UTIL]: Found component UTIL
-- Found XCB_UTIL: /usr/lib/libxcb-util.so  
-- XCB[IMAGE]: Found component IMAGE
-- Found XCB_IMAGE: /usr/lib/libxcb-image.so  
-- Found XCB: /usr/lib/libxcb.so;/usr/lib/libxcb-icccm.so;/usr/lib/libxcb-ewmh.so;/usr/lib/libxcb-util.so;/usr/lib/libxcb-image.so  
-- Searching for xcbgen with python2
-- Searching for xcbgen with python2.7
-- Searching for xcbgen with python3
-- Searching for xcbgen with python
CMake Error at lib/xpp/CMakeLists.txt:55 (message):
  Missing required python module: xcbgen
```

O mesmo acontece para a `polybar-git`:

```
$ yay -S ploybar-git
...
...
-- Found PythonInterp: /home/daltonmatos/.pyenv/shims/python2.7 (found suitable version "2.7.15", minimum required is "2.7") 
-- XCB[XCB]: Found component XCB
-- Found XCB_XCB: /usr/lib/libxcb.so  
-- XCB[ICCCM]: Found component ICCCM
-- Found XCB_ICCCM: /usr/lib/libxcb-icccm.so  
-- XCB[EWMH]: Found component EWMH
-- Found XCB_EWMH: /usr/lib/libxcb-ewmh.so  
-- XCB[UTIL]: Found component UTIL
-- Found XCB_UTIL: /usr/lib/libxcb-util.so  
-- XCB[IMAGE]: Found component IMAGE
-- Found XCB_IMAGE: /usr/lib/libxcb-image.so  
-- Found XCB: /usr/lib/libxcb.so;/usr/lib/libxcb-icccm.so;/usr/lib/libxcb-ewmh.so;/usr/lib/libxcb-util.so;/usr/lib/libxcb-image.so  
-- Searching for xcbgen with python2
-- Searching for xcbgen with python2.7
-- Searching for xcbgen with python3
-- Searching for xcbgen with python
CMake Error at lib/xpp/CMakeLists.txt:55 (message):
  Missing required python module: xcbgen
```

O que esse erro está dizendo é que falta um módulo chamado `xcbgen` no python que o script de instalação está usando, nesse caso `python2.7.15`.

Nesse caso estou usando o [pyenv](https://github.com/pyenv/pyenv) que permite ter um controle **bem melhor** de qual python será usado e sem interferir com o python padrão que está instalado no Arch.

# Obtendo a versão do xcbgen para o pyhton escolhido

Descobri pesquisando que o pacote `xcb-proto` instala o módulo `xcbgen` para o python do Arch. O que fiz foi apenas copiar o código que está instalado em `/usr/lib/python3.7/site-packages/xcbgen` para o `site-packages` do python que eu quero usar, assim:

```
cp -a /usr/lib/python3.7/site-packages/xcbgen ~/.pyenv/versions/2.7.15/lib/python2.7/site-packages/
```

Depois disso tudo compilou como esperado e o binário final foi gerado em `build/bin/polybar`, dentro da pasta do código-fonte do polybar, ou instalado normalmente caso você esteja usando algum AUR helper.

Acho que o próximo desafio vai ser tentar descobrir qual a dificuldade de gerar um binário estático. Vamos ver.

Por enquanto continuo no caminho de encontrar uma statusbar que me ajude a sair do zero sem ter que procurar script pra tudo e dando continuidade à minha tentativa de migração de Gnome Shell para i3.
