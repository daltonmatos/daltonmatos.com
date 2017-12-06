:title: Preparando uma Yubikey 4 Nano para uso diário
:date: 2017-09-27
:status: draft
:author: Dalton Barreto
:slug: preparando-uma-yubikey-4-nano-para-uso-diario


Intro
=====

Até saber da existência de smartcards, eu carregava minha chave RSA no meu computador pessoal
e tinha uma chave para cada computador que eu usava, basicamene uma chave no trabalho e uma
chave em casa.

Meu primeiro interesse em smartcards nem foi para usar como storage para chaves criptográficas e sim
para fazer Multi-Factor Autentication. Nesse caso o primeiro fator é algo que eu "sei" (minha senha) e o
segundo fator é algo que eu "tenho", ou seja, o smartcard.

Só isso já me pareceu suficientemente interessante para querer ter um smartcard, quando descobri que
esse smartcard em especial era compatível com OpenPGP, aí eu passei a definitivamente qurer ter um e inicei
minha pesquisa para saber qual seria a dificuldade de usar esse smartcard de forma fluida em uma máquina
rodando Linux. No meu caso específico Arch Linux, mas acredito que funcione quem qualquer outro, basta adaptar
o nome dos pacotes no momento de instalar.

Esse post surgiu dessa pesquisa e aqui descrevo as caracteríscidas do smartcard que comprei junto com o paso-a-passo
que fiz para fazê-lo funcionar.


Primeiro contato com o smartcart
================================

O smartcard que escolhi é produzido pela Yubico. O modelo que escolhi foi o Yubico 4 Nano. Escolhi pelo fato ser
ser **minúsculo** e caber praticamente todo dentro da porta USB. Sendo desse tamanho, seria possível usar a chave
sem chamar tanto a atenção por ter algo plugado na porta USB durante todo o tempo.

Logo que você insere o smartcard na porta usb ele se identifica como um dispositivo de entrada:

```

usb 2-1: new full-speed USB device number 31 using xhci_hcd
input: Yubico Yubikey 4 OTP+U2F+CCID as /devices/pci0000:00/0000:00:14.0/usb2/2-1/2-1:1.0/0003:1050:0407.0016/input/input31
hid-generic 0003:1050:0407.0016: input,hidraw1: USB HID v1.10 Keyboard [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-1/input0
hid-generic 0003:1050:0407.0017: hiddev1,hidraw2: USB HID v1.10 Device [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-1/input1

```

A primeira validação de funcionamento já dá pra ser feita nesse momento. Abre um edit de texto qualquer e toque no smartcard, se
uma string for digitada no editor significa que seu smartcard já está em funcionamento. É essa funcionalidade que acabamos de
testar que vai nos dar a possibilidade de usá-lo como segundo fator (mais sobre isso logo adiante).

Funcionalidades que vamos usar com esse smartcard
=================================================

No decorrer desse texto vamos ver como usar algumas funcionalidades desse smartcard, essas são:

* One Time Password (OTP)
* OpennPGP (Encriptação/Assinatura digital/Autenticação)
* Challenge-Response, que pode ser considerado um segundo fator de autenticação mas sem precisar de acesso à internet.


Instalação dos pacotes necessários
==================================

 * yubikey-manager
 * yubikey-manager-qt
 * pcsc-tools libu2f-host

Nota: Os yubikey-manager está disponível no OSX atrvés do pacote ykman, que pode instalado com o homebrew

Depois de instalar os pacotes, reinicie o servico `pcscd` e re-insira seu smartcard.

Usando One Time Password (OTP)
==============================

Resumindo bem brevemente, o OTP funciona da seguiinte maneira:

Cada smartcad bem de fábrica com uma chave privada pré-vinculada. Essa chave fica nas mãos da Yubico
e apenas o seu smartcard é capaz de gerar conteúdos que podem ser checados com essa chave que está com eles.

Então um fluxo de autenticação usando essa funcionalidade funciona assim:

* Você entra no site onde quer se autenticar (Poder ser GMail, Github, etc).
* Coloca sua senha e avança
* Nesse ponto, o site vai pedir que você toque no seu smartcard.
* Quando você fizer esse toque, um conteúdo único é gerado e enviado ao site (como se fosse um teclado mesmo)
* Nesse momento, o site consulta a fabricante (Yubico) para saber se o conteúdo é autentico.
* Se a Yubico responder positivamente, sua autenticação é concluída com sucesso.

Como você configurou sua autenticação no Gmail (por exemplo) para usar seu smartcard específico, mesmo que uma pessoa
tenha a sua senha não conseguirá entrar a não ser que tenha **o seu** smartcard.


Como ele se identifica como um teclado, a primeira função já está pronta.
A função de OTP (One Time Password) já vem pré-configurada pelo a Yubico.
Pois ele já vem configurado para falar o protocolo CCID (https://en.wikipedia.org/wiki/CCID_(protocol).

Basta encostar o dedo na chave e ela vai gerar um conteúdo único. Essa funcionalidade é usada paa fazer da sua chave um segundo fator de
autenticação.

Uma forma de validar sua nova chave é indo até https://demo.yubico.com.

Na aba "Single Factor" você pode testar a funconalidade de OTP.

Usando a funcionalidade U2F (Universal Second Factor)
================================================

Para testar, vá até a página "Test your U2F Device", registre um usuário/senha qualquer e clique em Next.

Esses são os pacotes que precisei instlar para que o chrome suportasse esse dispositivo como um U2F.

pcsc-tools libu2f-host
systemctl restart pcscd

Remova e re-insira sua chave yubikey

Agora preencha um user/senha quaisquer e vá em Next. Nesse momento a página te mostra uma mensagem pedindo que você
encoste na sua chave, sim sua chave é também um botão touch. E nesse momento ela deve estar com o led piscando. Isso indica
que ela está aguardando por alguma interação sua.

Assi que você toca a chave, a página carrega e você verá uma mensagem de "Verified Device". Nesse momento você confirmou que
servidores da Yubico reconhecem sua chave como um disposiivo válido. Agora ela está pronta para ser configurada como
Second Authentication Factor em suas contas. Como exemplo, esse e o link da própria Yubico mostrando como configurar seu GMail
para usar sua chave. https://www.yubico.com/support/knowledge-base/categories/articles/how-to-use-your-yubikey-with-google/

E para o Github: https://help.github.com/articles/configuring-two-factor-authentication-via-fido-u2f/


Usando a funconalidade de Chanlenge Response
============================================

_i yubikey-manager yubikey-manager-qt

$ ykman-gui

Insira a chave e o manager já vai se conectar a ela e mostrar alguns dados. Na parte de "Features", vá em "Configure".
Ali vamos configurar o Slot2 para ser nosso Challenge Response. Clique em Configure para o Slot 2.

Nas opções onde você pode escolher qual será a função do Slot 2, escolha Challenge-Response, clique Next.

Nesse momento é quando você escolhe uma chave secreta de 40 bytes hexadecimais para ser gravada na sua key e ser usada para herar os resultados do Challenge-Response. Clique em Generate. Marque a opção "Require Touch" e Clique em Finish.

Nesse momento você tem duas opções:

Você pode guardr essa chave secreta de 40 caracteres, dessa forma, se você precisar trocar de chave você poderá usar essa nova chave como se fosse a antiga, ou seja, todos os lugares onde você usou a antiga chave para Challenge-Response você vai poder usar a nova chave.

Ou você pode não guardar, mas nesse caso, quaisuqer dados que tiverem sido encriptados usando Challenge-response serão perdidos, caso sua chave pare de funcionare você precise substituir.

Testando challenge-response
---------------------------

Podemos usar assim: ykchalresp -2 <string>

Ele retorna sempre a mesma resposta, para uma mesma <string>

O que você pode fazer com isso é encriptar dados usando o resuldado de um challenge-response para uma <string> qualquer, ou seja, essa encriptação terá dois fatores de check: A <string>, que é sua senha + sua yuibkey, já que a verdadeira senha usada na encriptação final é o resultado do challenge-response.

Mostrar um exmeplo com `gpg --symmetric`. Talvez mostrar o script que escrevi pra fazer encript/decript usando challenge-response.

Citar que um outro uso seria encriptação de disco com LUKS. Assim para decriptar o disco você precisaria da seha, da yubikey e de um touch na chave.

Usando a Funcionalidade OpenPGP
===============================

O GnuPG depende da instalação do `yubikey-manager` para funcinar.

Para ver como está sua chave, digite:

$ gpg --card-status

Isso vai te dar algumas informações sobre a funcionalidade OpenPGP da sua chave. Agora que confirmamos que o GnuPG consegue
falar com ela, é hora de gerar suas chaves e grava-lasem sua chave yubikey.

Explicar a importância de poder ter sua chave privada sempre com você e de forma segura.
Explicar que o PIN e Admin PIN default são 123456 e 12345678.
Apontar para docs do gnupg onde mostra como trocar esses PINs.
Apontar para docs que mostram com gerar uma par de chaves GnuPG
Explicar como mantenhouma cópia da minha master key, fora do meu PC, mas de forma segura:
   - Gerei 256bits de dados randômiccos
   - Encripteri esses dados de duas formas:
     - Uma passphrase muito longa (+- 20 palavras)
     - Segunda passphrase: Resultado do challenge response da yubikey com uma string de 8 digitos
        - Assim posso decriptar minha master key de forma conveninente, usando uma passphrase menor (mais fácil de digitar) mas com um "salt" sendo a própria yubikey. Se a yubikey eventualmente morrer, uso a outra passphrase enquanto não compro outra key.

Explicar queé possível ativar a funcionalidade de "touch to sign", o que aumenta a segurança pois mesmo que algum código alicioso já esteja rodando no seu PC, elenão vai conseguir assinar/decriptar nada seu, pois a yubikey vai exigir um toque **físico** antes de qualquer opreção de criptografia.








