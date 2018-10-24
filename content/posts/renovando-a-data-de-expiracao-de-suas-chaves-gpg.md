---
title: Renovando a data de expiração de suas chaves GPG
author: Dalton Barreto
date: 2018-10-23
tags: [gnupg, gpg, crypt, pass]
---

Escolhi uma data de expiração de 6 meses para minhas chaves GPG. Penso nisso como uma forma de "prova de vida", onde a comprovação que eu ainda
mantenho o controle da chave privada é o fato de eu poder renovar a data de expiração de cada uma das chaves GPG.

Eis que chegou hora de fazer a primeira renovação (desde que adotei essa ideia de expirar as chaves de tempos em tempos). Aqui vamos ver o passo a passo de como podemos fazer essa renovação. E como isso afeta as [chaves que estão no smarcartd]({{<relref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md">}}).



# Usando o GnuPG em uma pasta não padrão

Para trocar as datas você precisa estar de posse da chave privada, para isso restaure o backup das suas chaves em um pasta qualquer e aponte o `gnupg` pra lá.

```
$ pwd                                            
/home/daltonmatos/.gpg
$ export GNUPGHOME=./gnupg
$ gpg -K           
/home/daltonmatos/.gpg/./gnupg/pubring.kbx
------------------------------------------
sec   rsa4096/389D4E1EC7F29FEF 2017-02-04 [SC]
      26A166B648B4863E96176558389D4E1EC7F29FEF
      Keygrip = 128DFDE36E82F2403A8CCBFC7A008DFC33A396E4
uid                 [ultimate] Dalton Barreto <daltonmatos@gmail.com>
uid                 [ultimate] Dalton Barreto <dalton.matos@sieve.com.br>
uid                 [ultimate] Dalton Barreto <dalton.matos@b2wdigital.com>
ssb   rsa4096/3B147A3234E02C43 2017-02-04 [S]
      Keygrip = 1A064CBF467D9EC6BE7C5D082A5E0514E3C9E432
ssb>  rsa4096/05570C19E57F6BB4 2017-05-16 [S] [expires: 2018-10-30]
      Keygrip = 0C2183A16531119C0BC5272089C435783E9BE339
ssb>  rsa4096/45768D9D6F14D474 2017-09-14 [E] [expires: 2018-10-30]
      Keygrip = 74CF1AF6F457AB8FF459B1FAD69EFAD2610A94A0
ssb>  rsa4096/AB8F87FDAD12AD6E 2017-09-14 [A]
      Keygrip = B12ECF12A5BCD345013AFBB459BF262E9F40B5C8
```

Aqui vemos que estou usando a pasta `/home/daltonmatos/.gpg/./gnupg/` como sendo meu keyring. Ali dentro está o backup das minhas chaves privadas.

Agora que confirmamos que o `GnuPG` está olhando para o lugar correto, podemos editar as chaves.

# Trocando as datas

Aqui vamos usar a edição normal de chaves:

```
$gpg --edit-key daltonmatos@gmail.com
gpg (GnuPG) 2.2.10; Copyright (C) 2018 Free Software Foundation, Inc.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.

Secret key is available.

sec  rsa4096/389D4E1EC7F29FEF
     created: 2017-02-04  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/3B147A3234E02C43
     created: 2017-02-04  expires: never       usage: S   
ssb  rsa4096/05570C19E57F6BB4
     created: 2017-05-16  expires: 2018-10-30  usage: S   
     card-no: 0006 06250168
ssb  rsa4096/45768D9D6F14D474
     created: 2017-09-14  expires: 2018-10-30  usage: E   
     card-no: 0006 06250168
ssb  rsa4096/AB8F87FDAD12AD6E
     created: 2017-09-14  expires: never       usage: A   
     card-no: 0006 06250168
[ultimate] (1). Dalton Barreto <daltonmatos@gmail.com>
[ultimate] (2)  Dalton Barreto <dalton.matos@sieve.com.br>
[ultimate] (3)  Dalton Barreto <dalton.matos@b2wdigital.com>
```

Percebam que as chaves `rsa4096/05570C19E57F6BB4` e `rsa4096/45768D9D6F14D474` possuem data de expiração.

Agora selecionamos quais chaves queremos mexer, fazemos isso com o comando `key`.

```
gpg> key 2
gpg> key 3
gpg> list

sec  rsa4096/389D4E1EC7F29FEF
     created: 2017-02-04  expires: never       usage: SC  
     trust: ultimate      validity: ultimate
ssb  rsa4096/3B147A3234E02C43
     created: 2017-02-04  expires: never       usage: S   
ssb* rsa4096/05570C19E57F6BB4
     created: 2017-05-16  expires: 2019-01-16  usage: S   
     card-no: 0006 06250168
ssb* rsa4096/45768D9D6F14D474
     created: 2017-09-14  expires: 2019-01-16  usage: E   
     card-no: 0006 06250168
ssb  rsa4096/AB8F87FDAD12AD6E
     created: 2017-09-14  expires: never       usage: A   
     card-no: 0006 06250168
[ultimate] (1). Dalton Barreto <daltonmatos@gmail.com>
[ultimate] (2)  Dalton Barreto <dalton.matos@sieve.com.br>
[ultimate] (3)  Dalton Barreto <dalton.matos@b2wdigital.com>
```

Agora que as duas chaves corretas estão selecionadas, usamos o comando `expire`:

```
gpg> expire
Are you sure you want to change the expiration time for multiple subkeys? (y/N) y
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0) 
```

E aqui você escolhe o novo período de expiraçao das suas chaves. Depois disso apenas digite `save` e saia do `GnuPG`.


# Importando a nova chave pública

Agora que temos as chaves modificadas, precisamos re-exportar nossa chave pública e re distrirbuí-la. Para isso rode:

```
$ gpg --export daltonmatos@gmail.com
```

Isso vai gerar uma nova cópia da sua chave púbica, com as datas atualizadas.


# Impacto nas chaves que estão dentro do smartcard

No meu caso tenho minhas chaves privadas dentro de um smarcartd. Nesse momento ele está indicando que as chaves estão perto de expirar, mostrando a data `2018-10-30`.

```
$ gpg --card-status

Reader ...........: <redacted>
Application ID ...: <redacted>
Version ..........: 2.1
Manufacturer .....: Yubico
Serial number ....: <redacted>
Name of cardholder: Dalton Barreto
Language prefs ...: br
Sex ..............: male
URL of public key : https://daltonmatos.com/daltonmatos.pub
Login data .......: daltonmatos
Signature PIN ....: not forced
Key attributes ...: rsa4096 rsa4096 rsa4096
Max. PIN lengths .: 127 127 127
PIN retry counter : 3 0 3
Signature counter : 5167
Signature key ....: CD07 76B0 E29F 585E BD3F  5E92 0557 0C19 E57F 6BB4
      created ....: 2017-05-16 23:21:41
Encryption key....: 7360 120F DE66 3A8A 165A  0039 4576 8D9D 6F14 D474
      created ....: 2017-09-14 13:16:21
Authentication key: 6561 5742 10EF 27DA 42B3  4AC9 AB8F 87FD AD12 AD6E
      created ....: 2017-09-14 13:21:06
General key info..: sub  rsa4096/05570C19E57F6BB4 2017-05-16 Dalton Barreto <daltonmatos@gmail.com>
sec#  rsa4096/389D4E1EC7F29FEF  created: 2017-02-04  expires: never     
ssb#  rsa4096/3B147A3234E02C43  created: 2017-02-04  expires: never     
ssb>  rsa4096/05570C19E57F6BB4  created: 2017-05-16  expires: 2018-10-30
                                card-no: 0006 06250168
ssb>  rsa4096/45768D9D6F14D474  created: 2017-09-14  expires: 2018-10-30
                                card-no: 0006 06250168
ssb>  rsa4096/AB8F87FDAD12AD6E  created: 2017-09-14  expires: never     
                                card-no: 0006 06250168

```

Mas basta eu importar minha chave recém criada (com as datas atualizadas):

```
$ gpg --import ~/src/daltonmatos.com/static/daltonmatos.pub 
gpg: key 389D4E1EC7F29FEF: public key "Dalton Barreto <daltonmatos@gmail.com>" imported
gpg: Total number processed: 1
gpg:               imported: 1
```

E a partir de agora, o `GnuPG` já mostra as datas novas no status do smartcard:

```
$ gpg --card-status                                        

Reader ...........: <redacted>
Application ID ...: <redacted>
Version ..........: 2.1
Manufacturer .....: Yubico
Serial number ....: <redacted>
Name of cardholder: Dalton Barreto
Language prefs ...: br
Sex ..............: male
URL of public key : https://daltonmatos.com/daltonmatos.pub
Login data .......: daltonmatos
Signature PIN ....: not forced
Key attributes ...: rsa4096 rsa4096 rsa4096
Max. PIN lengths .: 127 127 127
PIN retry counter : 3 0 3
Signature counter : 5167
Signature key ....: CD07 76B0 E29F 585E BD3F  5E92 0557 0C19 E57F 6BB4
      created ....: 2017-05-16 23:21:41
Encryption key....: 7360 120F DE66 3A8A 165A  0039 4576 8D9D 6F14 D474
      created ....: 2017-09-14 13:16:21
Authentication key: 6561 5742 10EF 27DA 42B3  4AC9 AB8F 87FD AD12 AD6E
      created ....: 2017-09-14 13:21:06
General key info..: sub  rsa4096/05570C19E57F6BB4 2017-05-16 Dalton Barreto <daltonmatos@gmail.com>
sec#  rsa4096/389D4E1EC7F29FEF  created: 2017-02-04  expires: never     
ssb#  rsa4096/3B147A3234E02C43  created: 2017-02-04  expires: never     
ssb>  rsa4096/05570C19E57F6BB4  created: 2017-05-16  expires: 2019-01-16
                                card-no: 0006 06250168
ssb>  rsa4096/45768D9D6F14D474  created: 2017-09-14  expires: 2019-01-16
                                card-no: 0006 06250168
ssb>  rsa4096/AB8F87FDAD12AD6E  created: 2017-09-14  expires: never     
                                card-no: 0006 06250168
```

Uma outra forma de fazer, no meu caso, seria atualizar minha chave no meu site e fazer:

```
$ gpg --card-edit  


gpg/card> fetch
gpg: requesting key from 'https://daltonmatos.com/daltonmatos.pub'
gpg: key 389D4E1EC7F29FEF: "Dalton Barreto <daltonmatos@gmail.com>" imported
gpg: Total number processed: 1
gpg:              unchanged: 1
```

E a partir de agora as chaves estão com nova data de expiração.
