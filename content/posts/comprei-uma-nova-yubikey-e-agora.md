---
title: Comprei uma yubikey nova, e agora?
author: Dalton Barreto
draft: true
date: 2018-12-07
tags: [yubikey, crypt, gpg, gnupg]

---


Nesse POST vou descrever os passos que tenho que percorrer para preparar uma nova Yubikey para uso diário.

Recentemente comprei uma nova chave e chegou a hora de substituir minha chave atual por essa nova.

A chave nova é uma Yubikey 5 NFC, e resolvi trocar por alguns motivos:

* Possui NFC, ou seja, posso usar no celular sem precisar de nenhum tipo de adaptador. Atualmente carrego comigo um adaptador USB-A > USB-C;
* É a primeira chave da yubico que possui NFC e suporte a chaves GPG de 4096bits;
* Apesar da chave ser fisicamente um pouco maior ela já possui um furo que permite ser colocada diretamente na argola do meu molho chaves.


# Comunicando com a chave pela primeira vez

Quando inserimos a nova chave pela primeira vez, após [instalar os pacotes necessários]({{<relref "./configurando-yubikey-para-auth-sign-otp-u2f.md">}}) vemos que els está vazia:


```
$ gpg --card-status               
Reader ...........: 1050:0407:X:0
Application ID ...: D2760001240102010006090456150000
Version ..........: 2.1
Manufacturer .....: Yubico
Serial number ....: <redacted>
Name of cardholder: [not set]
Language prefs ...: [not set]
Sex ..............: unspecified
URL of public key : [not set]
Login data .......: [not set]
Signature PIN ....: not forced
Key attributes ...: rsa2048 rsa2048 rsa2048
Max. PIN lengths .: 127 127 127
PIN retry counter : 3 0 3
Signature counter : 0
Signature key ....: [none]
Encryption key....: [none]
Authentication key: [none]
General key info..: [none]
```


O que vamos preencher agora são os seguintes dados:

* Name of cardholder 
* Language prefs
* URL of public key
* Login data

Fazemos isso usando o `gpg --card-edit`.

```
$ gpg --card-edit
gpg/card> help
quit           quit this menu
admin          show admin commands
help           show this help
list           list all available data
fetch          fetch the key specified in the card URL
passwd         menu to change or unblock the PIN
verify         verify the PIN and list all data
unblock        unblock the PIN using a Reset Code
```

Aqui vemos os comandos básicos. O primeiro comando que vamos usar é o `verify`. Esse comando vai permitir que façamos uma checagem no PIN padrão que vem configurado na yubikey. Vamos trocar esse PIN mais tarde. O PIN padrão que vem em todas as yubikeys é: `123456`.

```
gpg/card> verify

Reader ...........: 1050:0407:X:0
Application ID ...: D2760001240102010006090456150000
Version ..........: 2.1
Manufacturer .....: Yubico
Serial number ....: 09045615
Name of cardholder: [not set]
Language prefs ...: [not set]
Sex ..............: unspecified
URL of public key : [not set]
Login data .......: [not set]
Signature PIN ....: not forced
Key attributes ...: rsa2048 rsa2048 rsa2048
Max. PIN lengths .: 127 127 127
PIN retry counter : 3 0 3
Signature counter : 0
Signature key ....: [none]
Encryption key....: [none]
Authentication key: [none]
General key info..: [none]
```

Assim que você digita `verify` no prompt e dá enter, a yubikey pedirá uma senha. Digite `123456` e se essa for mesmo a senha da yubikey os dados do cartão serão exibidos.
Se essa senha for recusada significa que sua yubikey já foi configurada por alguém. Se você tiver **certeza** de que essa yubikey é nova e nunca foi usada o mlehor é entrar em contato com o fabricante.

# Nota sobre o tamanho máximo da chave que pode ser movida para a yubikey

Obsereve a seguinte linha:

```
Key attributes ...: rsa2048 rsa2048 rsa2048
```
Essa linha indica o tipo e tamanho máximo de cada uma das chaves que sua yubikey suporta. Nesse caso as três chaves (sign/encrypt/auth) são do tipo `RSA` e com tamanho máximo de `2048` bits.

Se suas chaves são maiores do que esse tamanho, então antes você precisa ajustar os Key Attributes de sua yubikey. Para isso faça assim:

```
$ gpg --card-edit  

gpg/card> admin
Admin commands are allowed

gpg/card> key-attr 
Changing card key attribute for: Signature key
Please select what kind of key you want:
   (1) RSA
   (2) ECC
Your selection? 1
What keysize do you want? (2048) 4096
The card will now be re-configured to generate a key of 4096 bits
Changing card key attribute for: Encryption key
Please select what kind of key you want:
   (1) RSA
   (2) ECC
Your selection? 1
What keysize do you want? (2048) 4096
The card will now be re-configured to generate a key of 4096 bits
Changing card key attribute for: Authentication key
Please select what kind of key you want:
   (1) RSA
   (2) ECC
Your selection? 1
What keysize do you want? (2048) 4096
The card will now be re-configured to generate a key of 4096 bits

gpg/card> verify

Key attributes ...: rsa4096 rsa4096 rsa4096
```

Perceba agora que a indicação é `rsa4096`.


# Editando os dados básicos da sua yubikey

Os comandos que precisamos estão dentro do menu `admin`.

```
gpg/card> admin
Admin commands are allowed

gpg/card> help
quit           quit this menu
admin          show admin commands
help           show this help
list           list all available data
name           change card holder's name
url            change URL to retrieve key
fetch          fetch the key specified in the card URL
login          change the login name
lang           change the language preferences
sex            change card holder's sex
cafpr          change a CA fingerprint
forcesig       toggle the signature force PIN flag
generate       generate new keys
passwd         menu to change or unblock the PIN
verify         verify the PIN and list all data
unblock        unblock the PIN using a Reset Code
factory-reset  destroy all keys and data
kdf-setup      setup KDF for PIN authentication
key-attr       change the key attribute

gpg/card> 
```

Aqui vemos os comandos que vamos precisar usar:

* `name` para trocar o nome do Card holder;
* `lang` para trocar os dados de Language prefs;
* `url` para mudar o endereço da chave pública (veremos mais sobre isso adiante);
* `login` para mudar os dados sobre login.


Com isso em mãos podemos começar:

## Mudando no Nome do cardholder

```
$ gpg --card-edit

gpg/card> admin
Admin commands are allowed

gpg/card> name
Cardholder's surname: Barreto
Cardholder's given name: Dalton

gpg/card> 
```

Assim que você digita todas as informações a yubikey vai pedir uma senha, mas perceba que o que está pedindo agora **não é** o PIN e sim o **ADMIN PIN**. O ADMIN PIN padrão de toda yubikey nova é: `12345678`. Assim que você informa o ADMIN PIN correto os dados são salvos. Se rodarmos o comando `verify` novamente, vemos que agora o nome está preenchido:

```
gpg/card> verify

...
Name of cardholder: Dalton Barreto
...
```

Aqui coloquei apenas a parte do output que importa. Vamos seguir.

## Mudando Language prefs

```
gpg/card> lang
Language preferences: ptbr

gpg/card> verify

Language prefs ...: ptbr
```

## Mudando URL da chave pública

```
gpg/card> url
URL to retrieve public key: https://daltonmatos.com/daltonmatos.pub

gpg/card> verify

URL of public key : https://daltonmatos.com/daltonmatos.pub
```

Essa informação serve para que o gnuPG saiba onde está a chave pública que é o par da chave privada que está dentro a yubikey. Essa URL é útil quando estamos em uma máquina que ainda não possui nossa chave pública.

Para que o próprio gnuPG busque nossa chave pública e instale localmente, veja:

```
$ gpg --card-edit  

gpg/card> fetch
gpg: requesting key from 'https://daltonmatos.com/daltonmatos.pub'
gpg: key 389D4E1EC7F29FEF: "Dalton Barreto <daltonmatos@gmail.com>" not changed
gpg: Total number processed: 1
gpg:              unchanged: 1

gpg/card> 
```

Dessa forma, a chave pública estaria corretamente instalada.

## Mudando login data

```
gpg/card> login
Login data (account name): daltonmatos

gpg/card> verify

Login data .......: daltonmatos
```

# Movendo duas chaves pra dentro da sua yubikey

Agora é a hora de mover a parte mais importante:  Suas chaves. Para isso precisamo [accessar nosso backup]({{<relref "./o-que-acontece-se-minha-yubikey-parar-de-funcionar.md">}}) para podermos pegar uma cópia dessas chaves e poder movê-las para dentro da yubikey.

O que faço nesse ponto é o seguinte:

* Acesso meu backup e descompacto ele em um lugar qualquer, por exemplo: `/tmp/keys`;
* Faço `export GNUPGHOME=/tmp/keys`;
* Uso o GnupG para move as chaves.

Para isso preciamos agora editar a chave que queremos move:
```

gpg --edit-key daltonmatos@gmail.com
gpg (GnuPG) 2.2.11; Copyright (C) 2018 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Secret key is available.

sec  rsa4096/389D4E1EC7F29FEF
     created: 2017-02-04  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/3B147A3234E02C43
     created: 2017-02-04  expires: never       usage: S   
ssb  rsa4096/05570C19E57F6BB4
     created: 2017-05-16  expires: 2019-01-16  usage: S   
     card-no: 0006 06250168
ssb  rsa4096/45768D9D6F14D474
     created: 2017-09-14  expires: 2019-01-16  usage: E   
     card-no: 0006 06250168
ssb  rsa4096/AB8F87FDAD12AD6E
     created: 2017-09-14  expires: never       usage: A   
     card-no: 0006 06250168
[ultimate] (1). Dalton Barreto <daltonmatos@gmail.com>
```

Aqui vamos usaar o comando `keytocard`, isso vai **mover** a chave privada para a yubikey.


Primeiro precisamos escolher qual sub-chave quremos mover. Vamos começar pela sub-chave `rsa4096/05570C19E57F6BB4`. Para isso vamos selecioná-la com o comando `key`.

```
gpg> key 2

sec  rsa4096/389D4E1EC7F29FEF
     created: 2017-02-04  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/3B147A3234E02C43
     created: 2017-02-04  expires: never       usage: S   
ssb* rsa4096/05570C19E57F6BB4
     created: 2017-05-16  expires: 2019-01-16  usage: S   
     card-no: 0006 06250168
ssb  rsa4096/45768D9D6F14D474
     created: 2017-09-14  expires: 2019-01-16  usage: E   
     card-no: 0006 06250168
ssb  rsa4096/AB8F87FDAD12AD6E
     created: 2017-09-14  expires: never       usage: A   
     card-no: 0006 06250168
```

Com a sub-chave correta selecionada (repare o `*` indicando a seleção), podemos movê-la. Para mover basta usar o comando `keytocard`. A cada sub-chave o gnupg vai perguntar para qual slot você deseja mover, nesse momento você deve escolher o slot correspontende à capacidade da sua sub-chahve: Assinatura, Encriptação ou Autenticação.

# Mudando o PIN e Admin PIN

Agora chegou a hora de mudar os PINs defaut. Para isso edite o cartão e use o comando `passwd`:

```
gpg/card> admin
Admin commands are allowed

gpg/card> passwd
gpg: OpenPGP card no. D2760001240102010006090456150000 detected

1 - change PIN
2 - unblock PIN
3 - change Admin PIN
4 - set the Reset Code
Q - quit

Your selection? 
```

Agora basta selecionar a opção desejada. A cada PIN mudado você deverá fornecer o PIN atual e o novo PIN.

Agora sua nova yubikey está pronta pra uso!

