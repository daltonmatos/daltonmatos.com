---
title: So long LastPass and thank you for all the fish
date: 2018-09-14
author: Dalton Barreto
tags: [mfa, pass, 2fa]
---

Desde que pude [guardar minha chave GPG de forma segura em um token físico]({{<relref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md" >}}), passei a pensar em como voltar a ter controle sobre minhas informações já que agora posso guardá-las encriptadas com essa chave.

Os primeiros dados que comecei a encriptar foram documentos sensíveis que guardo de backup, como comprovantes, documentos pessoais e afins.

O segundo passo foi fazer algo em relação ao password manager. Uso o [LastPass](https://lastpass.com) já há muito tempo e sempre funcionou muito bem, cumpriu seu propósito.

Mas a ideia de mudar de password manager surgiu quando comecei a querer tentar ter o total controle sobre os dados e também ter a certeza de que eles estão encriptados com a [minha chave GPG]({{<relref path="/gpg">}}). No caso do LastPass a senhas estão encriptadas, mas com uma senha que eu tenho que lembrar. Fazendo essa migração e tendo as senhas encriptadas com minha chave GPG eu poderia ter a senha do LastPass nesse novo password manager, logo seria uma senha a menos para me lembrar.

Continuando no caminho de ter que lembrar do mínimo de senhas possível, ter minha senhas encriptadas com minha chave GPG (que está em um smartcard e protegida pela única senha que quero ter que lembrar) parecia (e ainda parece!) uma boa ideia.

# Pass

Pesquisando sobre soluções que pudessem me fornecer o que eu precisava achei o projeto do [pass](https://passwordstore.org) que não só faz o que eu queria, mas faz algmas coisas a mais, tais como:

* Os dados são gravados em um repositório Git;
* Permite usar múltiplas chaves GPG para encriptar as senhas, podendo escolher quais grupos de senhas são encriptadas com quais chaves. Ou seja, posso ter senhas compartilhadas com outra(s) pessoa(s) sem precisar expor minha chave privada, basta ter a chave pública dessa pessoa.
* Possui suporte a plugins. Dentre eles o mais interessante até agora e parte do "kit básico" é o [pass-otp](https://github.com/tadfisher/pass-otp#readme)

Existe uma extensão para Chrome que é um wrapper para o `pass`, o que permite acessar suas senhas de forma **muito fácil** de dentro do browser, isso também era essencial para que o uso no dia a dia não ficasse prejudicado. Falaremos dessa extensão já já.

O fato de ser uma command line application também abre inúmeras possibilidades de integração com scripts ou mesmo outros programas.

# Pass: Principais conceitos

O projeto é formato por apenas um comando: `pass`. Através dele você consegue manipular todas as entradas que tiverem sido criadas.

Por padrão, a senhas estão gravadas em `~/.password-store` e essa pasta é um repositório Git. Isso já é a primeira vantagem pois permite que você tenha esses dados em múltiplos dispositivos. Eu, por exemplo, tenho no meu computador pessoal, no computador do trabalho e no celular.

# Estrutura do ~/.password-store

A estrutura é simples. Você pode criar quantos níveis de pasta você quiser, mas a última pasta da árvore representa o site e as entradas dentro dessa pasta representam os múltiplos logins que você tem nesse site, vejamos um exemplo:

```
$ pass social/
social
├── facebook.com
│   └── user@server.com
├── instagram.com
│   └── user
└── twitter.com
    └── user@host.com
```

Nesse caso temos uma pasta. `social/` e dentro dela temos tres "sites". Cada site possui um usuário cadastrado. Como disse antes, essa estrutura você pode escolher como vai criar.

## Formato de cada umas das entradas

O "formato" de cada entrada criada com o `pass` é bem simples.

Cada entrada é um arquivo texto, comum. A primeira linha **sempre** é a senha. Após essa linha você pode gravar quaisquer informações que você quiser e que sejam relacionadas a essa entrada. Segue um exemplo:

```
pass coding/github.com/user@mail.com
130da4ef-41a5-4825-878b-7746a01e689c

Backup Codes:
1. XXXXXXXX
2. XXXXXXXX
3. XXXXXXXX
4. XXXXXXXX
```

Nesse output, a primeira linha é a senha e temos, a título de exmeplo, os Backups Codes dessa conta. Isso é apenas para mostrar que você pode guadar qualquer coisa dentro de uma entrada, não só a senha.

## Entradas encriptadas com múltiplas chaves

Se quisermos compartilhar essa senha com mais alguém, poderíamos fazer:

```
$ pass init -p coding/github.com/ GPGID1 GPGID2 ...
```

Fazendo isso, o `pass` iria re-encriptar todas as senhas dentro de `coding/github.com/` com as chaves GPG (`GPGID1 GPGID2 ...`) passadas na linha de comando.


## Plugin: pass-otp

Esse plugin é uma implementação possível para termos [MFA na linha de comando]({{<relref "./19a55b06-mfa-na-linha-de-comando.md">}}). Com ele podemos gerar os mesmos tokens que tínhamos no celular, só que sem precisar pegar o celular toda hora que formos fazer login nas contas.

Para inserir uma configuração OTP em uma entrada qualquer faça o seguinte:

```
$ pass otp append -s -i <TOTPKEY> <pass-name>
```

Onde `<TOTPKEY>` é a chave privada que está codificada no QRcode (que você escanearia com o Authenticator App) e `<pass-name>` é a entrada para a qual você quer adicionar a configuração TOTP.

A partir de agora, sempre que preciarmos de um token OTP para alguma conta, basta usar:

```
$ pass otp <pass-name>
```

E teremos um token gerado que podemos usar **com sucesso** no processo de login.

Se você precisar/quiser registrar esse mesmo TOTP no ceular, basta pedir ao `pass` que gere o QRcode original, assim:

```
$ pass otp uri -q <pass-name>
```

Nesse momento ele vai te mostrar o QRcode e você pode escanear normalmente com a App do celular.

## Extensão do Browser: browserpass

Existe também uma extensão pro Chrome (e Firefox) que permite ler as senhas do `pass` direto de dentro do browser. A extensão é a [browserpass](https://github.com/browserpass/browserpass).

O uso é bem simples: `Ctrl+Shift+L` ativa a extensão e permite que você faça uma busca. Depois que você selecionar a entrada desejada: `Shift+C` copia o usuário e `Ctrl+C` copia a senha.

Essa extensão também tem suporte a `TOTP`, então a través dela você também consegue gerar os tokens MFA para poder concluir seu login, tudo isso sem sair do browser. Na real, você consegue pegar essas três informações (User, Senha e Token OTP) sem nem encostar no mouse.


Usando o `pass` tenho a certeza de que minhas senhas estão encriptadas com minha chave (ou quaisquer outras que **eu** tiver escolhido) e eu posso, a partir desse momento, não saber mais uma senha, a do LastPass (Caso eu ainda use para guardar alguma coisa).
