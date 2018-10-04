---
title: Como armazeno de forma segura meus dados sensíveis de acessos a contas online
author: Dalton Barreto
date: 2018-10-04
tags: [pass, yubikey, gpg, mfa, 2fa]
---

Esse texto é uma descrição geral do [modelo de segurança]({{<relref "./modelo-de-seguranca-para-uso-de-uma-yubikey.md">}}) que escolhi usar depois de pesquisar sobre como outras pessoas guardam dados sensíveis de forma segura.

A motivação principal, além de poder ter os dados guardados de forma segura (e aprender muito sobre esse assunto), foi poder ter o total controle sobre eles.

Se você usa um password manager online por exemplo, o mínimo que você deveria fazer seria manter esses dados encriptados. Afinal, se estiverem nas mãos de uma empresa qualquer que pelo menos estejam codificados com chaves que só você tem.

# Confiança na criptografia

Tudo que estamos fazendo aqui gira em torno de uma boa criptografia. No dia em que a criptografia que você escolheu for quebrada, você está basicamente perdido. Talvez um dos caminhos seja re-encriptar seus dados usando uma criptografia mais forte e torcer para as cópias antigas não caírem nas mãos de quem sabe quebrar a criptografia anterior. Renovar todas as senhas (ou pelo menos as mais críticas) se torna bem importante também.

# Dados nas mãos de terceiros

Ter seus dados nas mãos de terceiros não é, necessariamente, um problema. O problema começa quando esse terceiro sofre algum tipo de vazamento de informações.

Boa parte da minha motivação de fazer essa migração foi gravar meus dados de uma forma que eu tenha **certeza** de que eles estão encriptados, e não só isso, que eles estejam encriptados **apenas** com as chaves que **eu** escolhi.

Quando sou eu quem escolhe as chaves que serão usadas preciso [guardá-la de forma segura]({{<relref "./modelo-de-seguranca-para-uso-de-uma-yubikey.md#gerando-sua-chave-gpg">}}).

# Authenticator App

O primeiro passo na migração foi [trocar de Authenticator App]({{<relref "./19a55b06-mfa-na-linha-de-comando.md#totp-na-linha-de-comando">}}). Usei o Google Authenticator por muito tempo, até começar a pensar: "O que aconteceria se perdesse meu telefone?

Quando percebi a dor de cabeça que isso me daria, comecei a procurar por outras apps que fariam o mesmo papel.

Foi quando descobri o [Authy](https://authy.com). A grande diferença dele é que ele faz backup dos seus tokens MFA e isso já é uma **grande** vantagem. Com ele, caso eu perdesse meu celular poderia recuperar o número junto à operadora, instalar o Authy novamente e meus tokens estariam novamente disponíveis para uso.

Aqui entra uma outra questão também, que é a operadora de telefonia. Se alguém conseguir (via engenharia social?) induzir a operadora a recuperar sua linha telefônica em um chip que **não é o seu**, esse chip terá acesso irrestrito aos seus tokens MFA. Poder guardar os tokens comigo me protege também dessa possibilidade.

Assim como no caso do password manager online o Authy guarda seus backups em um servidor remoto. E aqui vamos à questão de ter o controle sobre esses dados e termos a certeza de que estão bem guardados, não só em termos de proteção contra eventuais vazamentos mas também na questão de qual criptografia foi usada (e se foi usada alguma) para guardá-los.

## Tokens MFA gerados fora do Celular

Quando descobri a possibilidade de [gerar os tokens OTP na linha de comando]({{<relref "./19a55b06-mfa-na-linha-de-comando.md">}}) passei a não depender do celular para acessar minhas contas, mesmo as que estão com MFA habilitado.

Isso é ótimo e vai um pouco na contra-mão do que costumamos ver, que é uma dependência **total** da presença do celular e no momento em que esse celular (com o App de autenticação) é perdido começa uma longa caminhada para recuperar o acesso a **todas** as contas.

Exatamente por causa dessa dependência é que acho que surgiram Apps de autenticação como o Authy, que se dizem diferenciados por fazer o backup dos seus tokens MFA. Mas mesmo nesses casos, você ainda depende do celular para recuperar acesso ao seu Authy em caso de perda.

# Password Manager

A [troca de password manager]({{<relref "./so-long-lastpass-and-thank-you-for-all-the-fish.md">}}) veio logo em seguida. Mesmos motivos, agora tenho os dados guardados encriptados com **minha(s) chave(s)** e guardados de forma segura. Isso sem contar que não há transparência em relação a como esses dados eram guardados no password manager anterior. O máximo que era dito é que estavam "encriptados".

# Acesso aos dados no celular

O passo seguinte foi [poder ter acesso a tudo isso no celular]({{<relref "./uso-da-yubikey-no-android.md">}}). Com esse último passo consegui fechar todo o ciclo de uso dessas informações, pois agora posso acessar usando o PC ou usando o celular (caso esteja sem o PC no momento).

####### 

Olhando pra trás percebo que cheguei a um ponto onde o celular é irrelevante, pois nada está guardado lá. Na verdade transformei meu [smartcard]({{<relref "./configurando-yubikey-para-auth-sign-otp-u2f.md">}}) no ponto mais importante, e mesmo que ele seja perdido depende praticamente só de mim conseguir o acesso aos meus dados novamente.

A partir do [momento que perco meu smartcard]({{<relref "./o-que-acontece-se-minha-yubikey-parar-de-funcionar.md">}}) preciso começar o processo de retomar o acesso à minha [chave GPG]({{<relref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md">}}), depois disso volto **imediatamente** ao normal, com acesso completo a todas as minhas contas, como se nada tivesse acontecido.

