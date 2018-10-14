---
title: Criando sua keyring GPG de forma fácil
author: Dalton Barreto
date: 2018-10-14
tags: [gnupg, gpg, yubikey, pass, crypt]
---


Nesse texto preparei um forma fácil e semi-automatizada para que você possa criar sua keyring GPG. Em vez
de criar tudo usando o prompt interavido do [GnuPG](https://www.gnupg.org/) vamos usar uma funcionalidade que ele tem
e que permite que chaves sejam criadas a partir de arquivos de configuração. É o que ele mesmo chama de [Unattended GPG key generation](https://www.gnupg.org/documentation/manuals/gnupg/Unattended-GPG-key-generation.html).


# Estrutura da keyring

O que vamos fazer é criar 3 chaves, um para cada finalidade:

* Encriptação/Decriptação; (`encrypt`, `[E]`)
* Assinatura digital; (`sign`, `[S]`)
* Autenticação (SSH). (`auth`, `[A]`)

# Template inicial

Criando a chave principal + a chave de encriptação. Como o GnuPG só permite ciar **uma** sub-chave de forma semi-automatizada, precisaremos
criar essa chave primeiro e depois vamos criar as outras.

Esse é o template inicial. Esse template criará a chave principal mais uma sub-chave capaz de Encriptar.

```
%echo Generating a basic OpenPGP key

Key-Type: RSA
Key-Length: 4096
Key-Usage: sign
Name-Real: Dalton Barreto
Name-Email: daltonmatos@gmail.com
Expire-Date: 0
Preferences: CAMELLIA256 SHA512 SHA384 SHA256 SHA224 AES256 AES192 AES CAST5 ZLIB BZIP2 ZIP Uncompressed

Subkey-Type: RSA
Subkey-Length: 4096
Subkey-usage: encrypt

%commit
%echo done
```
**Notas**:

* Quando rodar o comando abaixo, será perguntada a Passphrase. Aqui é uma escolha sua ter uma senha para sua chave, ou não;
* Aqui usei `Exprire-Date: 0`. Caso queira escolher uma data de expiração, coloque aqui. Um exemplo: para expirar em 6 meses coloque `6m`.

Salve esse conteúdo em um arquivo e rode, na linha de comando:

```
$ gpg --batch --generate-key </caminho/para/o/arquivo/com/o/conteudo/acima>
gpg: keybox '/tmp/tmp.78eBuVusrk/pubring.kbx' created
gpg: Generating a basic OpenPGP key
gpg: /tmp/tmp.78eBuVusrk/trustdb.gpg: trustdb created
gpg: key DD83AB94915A267F marked as ultimately trusted
gpg: directory '/tmp/tmp.78eBuVusrk/openpgp-revocs.d' created
gpg: revocation certificate stored as '/tmp/tmp.78eBuVusrk/openpgp-revocs.d/FDAB9DF86F913B749FCD23E4DD83AB94915A267F.rev'
gpg: done
```

Esse é um output possível, principalmente se sua keyring nunca tiver sido inicializada antes.

Para olhar as chaves recém criadas rode `gpg -K`:

```
$ gpg -K
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
/tmp/tmp.78eBuVusrk/pubring.kbx
-------------------------------
sec   rsa4096 2018-10-14 [SC]
      FDAB9DF86F913B749FCD23E4DD83AB94915A267F
uid           [ultimate] Dalton Barreto <daltonmatos@gmail.com>
ssb   rsa4096 2018-10-14 [E]
```

Aqui já vemos as duas chaves criadas. A chave *master* e uma sub-chave para encriptação (`[E]`). Agora vamos criar mais duas chaves, uma para assinatura (`sign`) e uma para autenticação (`auth`).

## Criando as subkeys

Como não é possível criar mais de uma subkey usando esse template de configuração, vamos criar as subkeys adicionais na linha de comando. As configurações globais (ciphers, compression, hash) já estão escolhidas então precisamos escolher poucas opções para as sub-chaves.

O que temos que escolher para cada chave é:

* Algoritmo que será usado;
* Tamanho da chave;
* Data de expiração;
* Capacidade que chave terá. Criaremos uma chave para cada capacidade adicional: `sign` e `auth`.


Para adicionar uma nova sub-chave à chave que já criamos precisamos descobrir o fingerprint da chave principal. Descobrimos isso com: `gpg -K`.

```
$ gpg -K
gpg: checking the trustdb
gpg: marginals needed: 3  completes needed: 1  trust model: pgp
gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
/tmp/tmp.78eBuVusrk/pubring.kbx
-------------------------------
sec   rsa4096 2018-10-14 [SC]
      FDAB9DF86F913B749FCD23E4DD83AB94915A267F
uid           [ultimate] Dalton Barreto <daltonmatos@gmail.com>
ssb   rsa4096 2018-10-14 [E]
```

O seu fingerprint é esse ID que aparece logo abaixo das informações da chave *master*, nesse caso: `FDAB9DF86F913B749FCD23E4DD83AB94915A267F`.

Então vamos criar nossa chave para assinatura digital:

```
gpg --quick-add-key FDAB9DF86F913B749FCD23E4DD83AB94915A267F rsa4096 sign 6m
```

Aqui o parametros são: algoritmo+keysize (`rsa4096`), usage-type (`sign`) e data de expiração (`6m`). Aqui escolhi expirar essa chave em 6 meses, mas caso você omita esse parâmetro sua chave não terá data de expiração. A data de expiração é facilmente modificável, caso você precise extender essa data posteriormente.

e essa é a criação da última sub-chave, a que é capaz de autenticar:

```
gpg --quick-add-key FDAB9DF86F913B749FCD23E4DD83AB94915A267F rsa4096 auth 6m
```

E para visualizar todas as chaves:

```
gpg -K
/tmp/tmp.78eBuVusrk/pubring.kbx
-------------------------------
sec   rsa4096 2018-10-14 [SC]
      FDAB9DF86F913B749FCD23E4DD83AB94915A267F
uid           [ultimate] Dalton Barreto <daltonmatos@gmail.com>
ssb   rsa4096 2018-10-14 [E]
ssb   rsa4096 2018-10-14 [S] [expires: 2019-04-12]
ssb   rsa4096 2018-10-14 [A] [expires: 2019-04-12]
```

E agora temos nossa keyring pronta para ser usada, com uma chave para cada responsabilidade: Encriptação, Assinatura e Autenticação.

Fazendo dessa forma podemos expirar e rotacionar as chaves de forma independente.

A partir daqui é hora de fazer um backup da sua keyring e [guardá-lo de forma segura]({{<relref "./modelo-de-seguranca-para-uso-de-uma-yubikey.md">}}).


# Configurações mínimas para o gnupg

Uma configuração essencial para que possamos usar o gpg de uma forma agradável é adicionar algumas opções em seu arquivo `~/.gnupg/gpg.conf`. Essas opções são:

```
keyid-format long
armor
```

Especialmente o `armor` que serve para gerar outputs "ASCII-Friendly" na linha de comando. Sem essa opção os outputs são todos binários, o que torna inviável de copiar/colar.

# Exportando suas chaves públicas

Depois de ter sua keyring pronta é hora de exportar sua chave pública e começar a distrubí-la para que pessoas possam te enviar conteúdo encriptado, certificar as assinaturas digitais feitas por você e também te dar acesso remoto a servidores.

## Chave pública GPG

Para exportar sua chave rode:

```
$ gpg --export <email>
```

nesse nosso caso:

```
$ gpg --export --armor daltonmatos@gmail.com > chave.pub
```

**Nota**: Caso já tenha configurado seu `gpg.conf`, pode remover o `--armor` desse comando (e de todos os outros no futuro).

Aqui o arquivo `chave.pub` conterá sua chave pública GPG. Como exemplo [aqui está a minha]({{<relref "../gpg.md">}}).

## Exportando sua chave pública no formato openssh

Para exportar sua chave em um formato que pode ser diretamento usado com ssh server, rode:

```
$ gpg --export-ssh-key daltonmatos@gmail.com                                  
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCaejFQzR+ezk8Dz1MecJBmnMn2xrSmhcR5WhS/29+R0drc4ttc2Bq0b9VNM1WKEyH7dB0LZ6LbogXJT+h/yrsAl0v5cmgsQBt3kRmVE7Ig6s601gnZMvNLQA2Rq5CI/+q2AcxmJ/BnJMt42Tg3gx+hNZTnl8a8tyl9/HV5B5hEPH9Vc3ERW7eZDJ424pnr5+1O3bQdRGHX3kJMQozWOFeUZ7YPar5Qi/MlcY1Rqja1JEp+ddfCIIQkm72xLeIj07eUk8tYoegUREpcBZgdZGVxQuuVvTo2ThNtHc6o51VmjeoYeH2Pnn4W7EhU75q6gv7XfBME00sl8hKzaxeoN/WTbag7kO90ey3W0B7zVkX12hYeeV17nFVZ9mfhKSqA9kkhrs76QBNSuuPgOFrt6jn1osI3W2MYfEj0wxkmdGHXBPrkMh1hlMGwWCe2PvNBkyIC86bq/V6ynCJUiXJBc01aAFQNE10tp92oouKzDvw6CpRke+MvSxk0Z3fTBjPIUYdW+hoLhCAsYwmRV8V+N+46NHzZO5VMYgRW0tjbrpaf0rDz45oa8rD5q6R8ctg2e21wamyCfgKwPFQLoulUD8lz3sO0bZdNX4UAF6xLlprGl38CJz3IxPafiONz8Ok0eQLNUG5Rwbpr0RTL8LGsNk5PXlNEgqFK1YuXNSkCpvPPgw== openpgp:0xFB41DA06
```

Esse é o conteúdo que deve ser colocado na sua home, no servidor remoto, no arquivo `~/.ssh/authorized_keys`.

A partir daqui é uma opção sua manter as chaves privadas (que estão nesse momento dentro da sua keyring) no seu PC ou [movê-las para um smartcard]({{<relref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md">}}) e **apagar** do PC (mantendo apenas as cópias do backup).

# Limpando sua keyring

Se sua opção for usar um smartcard o jeito mais fácil de limpar sua keyring é simplesmente apagando toda a pasta `~/.gnupg` e re-importar sua própria chave pública. Para importar sua chave rode esse comando:

```
gpg --import < chave.pub
```

Onde `chave.pub` é a chave pública que você exportou no [passo anterior]({{<relref "#chave-pública-gpg">}}). Aliás esse é o comando que você usará para importar a chave pública de qualquer pessoa.
