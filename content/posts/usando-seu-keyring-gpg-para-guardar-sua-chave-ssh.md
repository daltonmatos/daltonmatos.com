---
title: "Usando seu keyring GPG para guardar sua chave SSH"
author: Dalton Barreto
date: 2018-08-12
tags: [linux, ssh, gpg, gnupg, yubikey, smartcard]
---

Por muito tempo tive minha chave privada SSH gravada dentro da minha `${HOME}`, geralmente em `.ssh/id_rsa`. Algum tempo atrás descobri que o GnuPG permite criar chaves com "propriedades" específicas, por exemplo, Encriptação, Assinatura, etc.

O que vamos usar aqui é a propriedade de Autenticação. Para criar essa chave, vamos adicionar uma nova subchave à nossa keyring GPG.

Estou assumindo aqui que você já possui uma keyring e que já tem uma chave GPG criada.

Para criar uma nova subchave, precisamos editar nossa chave atual.

```
gpg --expert --edit-key <KEY-ID>
```
Onde `<KEY-ID>` é o ID da sua chave principal. O `--expert` faz com que o GnuPG mostre mais opções na hora da criação da subchave.

```
$ gpg --expert --edit-key ID
gpg> addkey
This key is not protected.
Please select what kind of key you want:
   (3) DSA (sign only)
   (4) RSA (sign only)
   (5) Elgamal (encrypt only)
   (6) RSA (encrypt only)
   (7) DSA (set your own capabilities)
   (8) RSA (set your own capabilities)
Your selection?
```
Aqui vamos escolher a opção `8`, pois vamos criar uma chave `RSA` e precisaremos escolher suas propriedades.

```
Possible actions for a RSA key: Sign Encrypt Authenticate
Current allowed actions: Sign Encrypt

   (S) Toggle the sign capability
   (E) Toggle the encrypt capability
   (A) Toggle the authenticate capability
   (Q) Finished

Your selection?
```

A linha "Current allowed actions: Sign Encrypt" mostra que a chave que está sendo criada possui duas propriedades: `Sign` e `Encrypt`. Vamos usar o menu para remover essas duas propriedades e adicionar a propriedade `Authenticate`. Fazemos isso usando as opções do menu exibido pelo GnuPG2.

Depois que estivermos terminado, basta usar a opção `Q` para continuar com a criação da nova chave.

No menu seguinte vamos escolher o tamanho da nova chave. Escolha `4096`.

```
RSA keys may be between 1024 and 4096 bits long.
What keysize do you want? (2048) 4096
```

Depois escolha a data de expiração. Aqui pode escolher o que fizer mais sentido para você.

```
Please specify how long the key should be valid.
         0 = key does not expire
      <n>  = key expires in n days
      <n>w = key expires in n weeks
      <n>m = key expires in n months
      <n>y = key expires in n years
Key is valid for? (0)
```
Confirme os próximos menus e o GnuPG começará a criar sua chave. Depois que estiver de volta ao prompt principal do GnuPG, digite `q` e confirme caso seja perguntado se quer salvar as alterações.

Nesse momento temos uma chave capaz de autenticar e que pode ser usada em sessões SSH.

# ssh-agent

O `ssh-agent` é um programa adicional que consegue gerenciar suas chaves privadas e cachear suas passphrases (se configurado pra isso). O grande lance aqui é que o comando `ssh` passa a não se importar mais de onde a chave privada está vindo, o que ele faz é apenas "conversar" com o agent pedindo que o acesso seja feito e o agent é quem lida com a chave para que o acesso aconteça.



## Configurando GnuPG como ssh-agent

Essa configuração é feita em dois lugares. Um é o `gpg-agent.conf` (esse arquivo fica na home do GnuPG, que está em `~/.gnupg/`) onde vamos apenas adicionar uma linha, assim:

```
enable-ssh-support
```

A segunda parte é indicar ao `ssh` onde está o socket do "ssh-agent", nesse caso, o gpg-agent se fazendo passar por ssh-agent.

Coloque isso no seu "shellrc" (.zshrc, .bashrc, etc), ou seja, deve ser importado sempre que você abrir um shell novo.

```
GPG_TTY=$(tty)
export GPG_TTY

if [ -z "${SSH_TTY}" ]; then
  export SSH_AUTH_SOCK="$(gpgconf --list-dirs agent-ssh-socket)"
fi
```

O `if` serve apenas para você não ativar o `gpg-agent` caso já esteja em uma sessão remota, dessa forma você pode usar esse mesmo "shellrc" em um servidor remoto, se quiser.

## Habilitando sua nova chave para ser usada pelo gpg-agent

As chaves que o gpg-agent oferece na conexões SSH ficam listadas no arquivo `~/.gnupg/sshcontrol`. Precisamos colocar ali, um por linha, o keygrip de cada uma das chaves que queremos usar.

Para pegar o keygrip da sua chave GPG, faça assim:

```
$ gpg -K --with-keygrip
...
ssb>  rsa4096/AB8F87FDAD12AD6E 2017-09-14 [A]
      Keygrip = B12ECF12A5BCD345013AFBB459BF262E9F40B5C8

```

Procure pela linha "Keygrip = ..." referente à subchave de autenticação que acabamos de criar. Um indicador `[A]` aparece na linha onde está o ID da sua chave. O keygrip da sua chave é o valor que está após o sinal de `=`.

Adicione esse valor no arquivo `sshcontrol` e a partir de agora ela será ofertada em todas as conexões SSH que você fizer.

Se você possuir mais de uma chave capaz de autenticar e quiser usá-la, precisará adicionar seu Keygrip no arquivo `sshcontrol`, em uma nova linha.



# Usando sua yubikey como chave privada SSH

Uma outra evolução possível desse setup é ter sua chave privada **fora** do seu computador, dentro de um smartcard PGP compatibile. A [Yubico](https://yubico.com) fabrica a [Yubikey 4 Nano](https://www.yubico.com/product/yubikey-4-series/#yubikey-4-nano), que é capaz de guardar sua chave privada de autenticação (entre outras).

Felizmente o GnuPG consegue se comunicar com esse smartcard, dessa forma ele com segue fornecer ao comando `ssh` a possibilidade de usar uma chave privada que está no cartão no momento fazer um acesso remoto. E é isso que vamos fazer.

## Movendo sua chave de autenticação para dentro do seu smartcard

Para que possamos usar nosso smartcard como chave privada SSH, primeiro temos que mover nossa chave de autenticação pra dentro do cartão.

Perceba que isso é uma operação que removerá sua chave privada do disco do seu computador, então se quiser guardar uma cópia do seu keyring GPG (você já fez isso né? ;-)), agora seria uma boa hora.

Para isso edite seu keyring:

```
$ gpg --edit-key KEY-ID
```

Dentro do menu de edição, selecione a chave que deseja mover com o comando `key N`, onde `N` é a chave que você quer, por exemplo: `key 1` seleciona a primeira chave, e assim por diante. Um `*` aparece ao lado da chave que foi selecionada. Caso tenha selecionado a chave errada, desfaça a seleção com o mesmo comando usado para selecionar e selecione a chave certa. Você pode também usar `key 0` para limpar todas as seleções.

Depois de selecionar, escolha o comando `keytocard`. Isso vai **mover** sua chave privada para seu smartcard.

Escolha o slot que seja compatível com a chave que está sendo movida e confirme.

Tendo sua chave privada SSH dentro do seu smartcard você pode, literalmente, levar sua chave ssh sempre com você em vez de depender de um PC específico que possui sua chave privada gravada no disco.

Sem contar que a Yibukey é um hardware feito específicamente para guardar conteúdo sensível de forma segura. Para usar o cartão você precisa ter uma senha de 8 dígitos, que se errada mais de 3 vezes (em sequência) bloqueiam o cartão. Nesse ponto você tem uma segunda senha, chamada de Admin PIN. Errando essa senha também 3 vezes, o cartão é **permanentemente invalidado**, ou seja, precisa ser re-inicializado. Pode ser usado normalmente de novo, mas o conteúdo que estava dentro dele foi perdido para sempre. Mas isso é assunto pra outro post.


# Usando outras chaves dentro de seu smartcard

Esse smartcard especificamente (Yubikey 4 Nano) permite também guardar outras 2 chaves: Encriptação e Assinatura.

O processo é o mesmo, abra sua keyring GPG e mova as chaves desejadas para o smartcard. Basta mover para o "slot" correto dentro do smartcard.

O próprio fabricante possui um texto bem detalhado sobre como usar seu smartcard com chaves GPG: https://support.yubico.com/support/solutions/articles/15000006420-using-your-yubikey-with-openpgp


