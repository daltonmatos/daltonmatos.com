---
title: Preparando uma Yubikey 4 Nano para uso diário
date: 2018-07-30
tags: [crypto, gpg, gnupg, smartcard, yubikey]
status: published
author: Dalton Barreto
slug: preparando-uma-yubikey-4-nano-para-uso-diario
---

Até saber da existência de smartcards, eu carregava minha chave RSA no meu computador pessoal
e tinha uma chave para cada computador que eu usava, basicamene uma chave no trabalho e uma
chave em casa.

Meu primeiro interesse em smartcards nem foi para usar como storage para chaves criptográficas e sim
para fazer Multi-Factor Autentication. Nesse caso o primeiro fator é algo que eu "sei" (minha senha) e o
segundo fator é algo que eu "tenho", ou seja, o smartcard.

Só isso já me pareceu suficientemente interessante para querer ter um smartcard, quando descobri que
esse smartcard em especial era compatível com OpenPGP, aí eu passei a definitivamente qureer ter um e iniciei
minha pesquisa para saber qual seria a dificuldade de usar esse smartcard de forma fluida em uma máquina
rodando Linux. No meu caso específico Arch Linux, mas acredito que funcione quem qualquer outro, basta adaptar
o nome dos pacotes no momento de instalar.

Esse post surgiu dessa pesquisa e aqui descrevo as caracteríscidas do smartcard que comprei junto com o paso-a-passo
que fiz para fazê-lo funcionar.


# Primeiro contato com o smartcart

O smartcard que escolhi é produzido pela [Yubico](https://yubico.com). O modelo que escolhi foi o [Yubico 4 Nano](https://www.yubico.com/product/yubikey-4-series/#yubikey-4-nano).
Escolhi pelo fato ser ser **minúsculo** e caber praticamente todo dentro da porta USB. Sendo desse tamanho, seria possível usar a chave
sem chamar tanto a atenção por ter algo plugado na porta USB durante todo o tempo.

Logo que você insere o smartcard na porta USB ele se identifica como um dispositivo de entrada:

```
usb 2-1: new full-speed USB device number 31 using xhci_hcd
input: Yubico Yubikey 4 OTP+U2F+CCID as /devices/pci0000:00/0000:00:14.0/usb2/2-1/2-1:1.0/0003:1050:0407.0016/input/input31
hid-generic 0003:1050:0407.0016: input,hidraw1: USB HID v1.10 Keyboard [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-1/input0
hid-generic 0003:1050:0407.0017: hiddev1,hidraw2: USB HID v1.10 Device [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-1/input1
```

A primeira validação de funcionamento já dá pra ser feita nesse momento. Abra um editor de texto qualquer e toque no smartcard, se
uma string for digitada no editor significa que seu smartcard já está em funcionamento. É essa funcionalidade que acabamos de
testar que vai nos dar a possibilidade de usá-lo como segundo fator (mais sobre isso logo adiante).

# Funcionalidades que vamos usar com esse smartcard

No decorrer desse texto vamos ver como usar algumas funcionalidades desse smartcard, são elas:

* One Time Password (OTP)
* OpennPGP (Encriptação/Assinatura digital/Autenticação)
* Challenge-Response, que pode ser considerado um segundo fator de autenticação mas sem precisar de acesso à internet.


# Instalação dos pacotes necessários

 * yubikey-manager
 * yubikey-manager-qt
 * pcsc-tools libu2f-host

Nota: O `yubikey-manager` está disponível no OSX atrvés do pacote `ykman`, que pode instalado via `homebrew`.

Depois de instalar os pacotes, reinicie o servico `pcscd` e re-insira seu smartcard.

# Usando One Time Password (OTP)

Resumindo bem brevemente, o OTP funciona da seguiinte maneira:

Cada smartcad vem de fábrica com uma chave privada pré-vinculada. Essa chave fica nas mãos da Yubico
e apenas o seu smartcard é capaz de gerar conteúdos que podem ser checados com essa chave que está com eles.

Então um fluxo de autenticação usando essa funcionalidade acontece assim:

* Você entra no site onde quer se autenticar (Poder ser GMail, Github, etc).
* Coloca sua senha e avança
* Nesse ponto, o site vai pedir que você toque no seu smartcard.
* Quando você fizer esse toque, um conteúdo único é gerado e enviado ao site (como se fosse um teclado mesmo)
* Nesse momento, o site consulta a fabricante (Yubico) para saber se o conteúdo é autentico.
* Se a Yubico responder positivamente, sua autenticação é concluída com sucesso.

Como você configurou sua autenticação no Gmail (por exemplo) para usar seu smartcard específico, mesmo que uma pessoa
tenha a sua senha não conseguirá entrar a não ser que tenha também **o seu** smartcard.


Como ele se identifica como um teclado, a primeira função já está pronta.
A função de OTP (One Time Password) já vem pré-configurada pelo a Yubico.
Pois ele já vem configurado para falar o [protocolo CCID ](https://en.wikipedia.org/wiki/CCID_(protocol).

Basta encostar o dedo na chave e ela vai gerar um conteúdo único. Essa funcionalidade é usada paa fazer da sua chave um segundo fator de
autenticação.

Uma forma de validar sua nova chave é indo até https://demo.yubico.com.

Na aba "Single Factor" você pode testar a funconalidade de OTP.

# Usando a funcionalidade U2F (Universal Second Factor)

Para testar, vá até a página "Test your U2F Device", registre um usuário/senha qualquer e clique em Next.

Esses são os pacotes que precisei instlar para que o chrome suportasse esse dispositivo como um U2F.

```
pcsc-tools libu2f-host
```

Reinicie o `pcscd`:

```
systemctl restart pcscd
```

Remova e re-insira sua chave yubikey

Agora preencha um user/senha quaisquer e vá em Next. Nesse momento a página te mostra uma mensagem pedindo que você
encoste na sua chave, sim sua chave é também um botão touch. E nesse momento ela deve estar com o led piscando. Isso indica
que ela está aguardando por alguma interação sua.

Assim que você toca a chave, a página carrega e você verá uma mensagem de "Verified Device". Nesse momento você confirmou que
servidores da Yubico reconhecem sua chave como um disposiivo válido. Agora ela está pronta para ser configurada como
Second Authentication Factor em suas contas. Como exemplo, esse é o link da própria Yubico mostrando como configurar seu GMail
para usar sua chave. https://www.yubico.com/support/knowledge-base/categories/articles/how-to-use-your-yubikey-with-google/

E para o Github: https://help.github.com/articles/configuring-two-factor-authentication-via-fido-u2f/


# Usando a funcionalidade de Challenge Response

Instale os seguintes pacotes:

```
yubikey-manager yubikey-manager-qt
```

Depis abra o yubikey mamager:

```
$ ykman-gui
```

Insira a chave e o manager já vai se conectar a ela e mostrar alguns dados. Na parte de "Features", vá em "Configure".
Ali vamos configurar o Slot2 para ser nosso Challenge Response. Clique em Configure para o Slot 2.

Nas opções onde você pode escolher qual será a função do Slot 2, escolha Challenge-Response, clique Next.

Nesse momento é quando você escolhe uma chave secreta de 40 bytes hexadecimais para ser gravada na sua key e ser usada para gerar os resultados do Challenge-Response. Clique em Generate. Marque a opção "Require Touch" e Clique em Finish.

Nesse momento você tem duas opções:

Você pode guardar essa chave secreta de 40 caracteres, dessa forma, se você precisar trocar de smartcard você poderá usar o novo smartcard como se fosse o antigo.

Ou você pode não guardar, mas nesse caso, quaisquer dados que tiverem sido encriptados usando Challenge-response serão perdidos,
caso seu smartcard pare de funcionare e/ou você precise substituir.

Testando challenge-response
---------------------------

Podemos usar assim: `ykchalresp -2 <string>`

Ele retorna sempre a mesma resposta, para uma mesma `<string>`

O que você pode fazer com isso é encriptar dados usando o resuldado de um challenge-response para uma `<string>` qualquer,
ou seja, essa encriptação terá dois fatores de check: A `<string>`, que é a senha que você "sabe", mais sua yubikey que é o **único** dispositivo capaz de gerar a saída correta
a partir da entrada que você digitou.

## Um exemplo simples

Digamos que quero encriptar com arquivo e quero dois fatores de autenticação nessa encriptação.
Vamos escolher o primeiro fator com sendo: `supersecret`.

Agora vamos usar o Challenge-Response que acabamos de configurar para gerar nossa senha real, que será usada na encriptação do arquivo:

```
$ ykchalresp -2 supersecret
6ad2ad635dbf37cbbabff2e1cdef2320fe909a49
```

Agora podemos encriptar nosso arquivo usando com senha o valor `6ad2ad635dbf37cbbabff2e1cdef2320fe909a49`. A partir de agora temos dois fatores de autenticação
pois a úncia forma de re-gerar essa senha que escolhemos é digitando o valor "supersecret" e entregando esse valor para nossa yubikey, que vai **sempre** geraro valor
`6ad2ad635dbf37cbbabff2e1cdef2320fe909a49`.


# Usando a Funcionalidade OpenPGP

O GnuPG depende da instalação do `yubikey-manager` para funcinar.

Para ver como está sua chave, digite:

```
$ gpg --card-status
```

Isso vai te dar algumas informações sobre a funcionalidade OpenPGP da sua chave. Agora que confirmamos que o GnuPG consegue
falar com ela, é hora de gerar suas chaves e grava-las em sua chave yubikey.

Não vamos detalhar aqui como gerar seu keyring GPG, pois existem muitos tutoriais bons por aí. Nem vamos detalhar como
mover suas chaves privadas para dentro do seu smartcard, pois a documentação do GnuPG é suficiente: https://wiki.gnupg.org/SmartCard

O que achei de mais interessante em relação a poder ter chaves GPG dentro do smartcard é que a partir de agora posso levar minhas chaves
comigo, no meu molho de chaves e não mais dentro de um computador. Agora não dependo mais de um PC específico para usar minhas chaves, pois
tenho elas sempre à mão.

Unindo isso ao fato do GnuPG permitir gerar chaves de autenticação, posso agora ter minha chave privada SSH também dentro do smartcard junto com 
duas outras chaves: Chave para assinatura digital e Chave para encriptação.

O uso do GnuPG é transparente, ou seja, você usa como se tivesse com suas chaves privadas no PC, mas na verdade estão no smartcard. Quando você usa
o GnuPG para mover as chaves privadas pro smartcard ele já sabe que elas estão lá e sempre que você precisa executar uma ação que dependa de uma de 
suas chaves privadas ele já faz a comunicação com o smartcard pra você.
