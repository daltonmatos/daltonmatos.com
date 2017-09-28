:title: Preparando ua Yubikey 4 Nano para uso diário
:date: 2017-09-27
:status: draft
:author: Dalton Barreto
:slug: preparando-uma-yubikey-4-nano-para-uso-diario

Pacotes Removidos
=================

 _u yubikey-manager python-pyscard pcsclite yubikey-manager-qt
checking dependencies...

Package (17)             Old Version  Net Change

libu2f-host              1.1.3-2       -0.13 MiB
python-asn1crypto        0.22.0-1      -1.16 MiB
python-cffi              1.10.0-1      -0.96 MiB
python-click             6.7-1         -0.66 MiB
python-cryptography      2.0.3-1       -2.21 MiB
python-ply               3.10-1        -0.31 MiB
python-pycparser         2.18-1        -1.24 MiB
python-pyopenssl         17.2.0-1      -0.51 MiB
python-pyotherside       1.5.0-3       -0.26 MiB
python-pyusb             1.0.0-5       -0.50 MiB
yubico-c                 1.13-4        -0.05 MiB
yubico-c-client          2.15-3        -0.07 MiB
yubikey-personalization  1.18.0-3      -0.19 MiB
pcsclite                 1.8.22-1      -0.29 MiB
python-pyscard           1.9.6-1       -0.89 MiB
yubikey-manager          0.4.4-1       -0.55 MiB
yubikey-manager-qt       0.3.1-1       -0.08 MiB

Total Removed Size:  10.05 MiB

dmesg ao inserir a chave na porta USB
=====================================


 input: Yubico Yubikey 4 OTP+U2F+CCID as /devices/pci0000:00/0000:00:14.0/usb3/3-2/3-2:1.0/0003:1050:0407.0003/input/input14
 hid-generic 0003:1050:0407.0003: input,hidraw2: USB HID v1.10 Keyboard [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-2/input0
 hid-generic 0003:1050:0407.0004: hiddev1,hidraw3: USB HID v1.10 Device [Yubico Yubikey 4 OTP+U2F+CCID] on usb-0000:00:14.0-2/input1

Usando OTP de fábrica
=====================

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








