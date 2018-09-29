---
title: Uso da Yubikey no Android
author: Dalton Barreto
date: 2018-09-29
tags: [yubikey, pass, gpg]
---

O último ponto que faltava na minha migração para um novo password manager era poder acessar meus dados usando o celular.

Aqui vou mostrar cada um dos apps que uso para poder ter o celular como uma ferramenta completa para poder usar meu smartcard.

# Suporte à yubikey 

Os smartcards da [Yubico](https://www.yubico.com/products/yubikey-hardware/) já são naturalmente suportados pelo Android. Os [smartcards que possuem NFC](https://www.yubico.com/products/yubikey-for-mobile/) têm suporte ainda melhor, pois basta aproximar o telefone do smartcard para que eles se comuniquem.

No meu caso tenho uma [Yubikey USB-A](https://www.yubico.com/product/yubikey-4-series/#yubikey-4-nano), então uso um adaptador USB-A > USB-C para poder usá-la no celular. Funciona muito bem.

**Nota**: Acredito que para funcionar plugado na USB do celular o aparelho precisa ter suporte a [USB OTG](https://en.wikipedia.org/wiki/USB_On-The-Go), que é o meu caso.

# Open Keychain

O [OpenKeyChain](https://www.openkeychain.org/) é o responsável por suportar o smartcard. Pense nele como uma espécie de "driver". Além de implementar suporte genérico ao uso de um smartcard, ele também implementa o necessário para que você consiga usar as funcionalidades relacionadas à chave GPG, ou seja, ele é capaz de assinar conteúdos, encriptar/decriptar dados usando a chave privada que está no smartcard.

Como o nome já diz ele é uma Keychain, isso significa que você pode importar chaves públicas de outras pessoas e isso te dá a possibilidade de trocar conteúdo encriptado com elas.

Além disso ele expõe uma API pública, dessa forma outros apps podem usar essa API e por isso podem também dar suporte ao uso de smartcards. É o caso do TermBot, que veremos a seguir.

# TermBot

Como tenho minha [chave SSH dentro do smartcard]({{<relref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md">}}) seria ideal poder ter um cliente SSH que fosse capaz de usar essa chave.

Existe um app que faz isso e é o [TermBot](https://play.google.com/store/apps/details?id=org.sufficientlysecure.termbot). O que ele faz, na verdade, é falar com a API do OpenKeyChain. Dessa forma tenho como fazer SSH para máquinas remotas usando a mesma chave que está dentro do smartcard.

# Password Store

O App [PasswordStore](https://github.com/zeapo/Android-Password-Store) é quem sabe ler os dados gravados [no password manager que uso]({{<relref "./so-long-lastpass-and-thank-you-for-all-the-fish.md">}}), o [pass](https://passwordstore.org).

Com esse App consigo sincronizar todos os dados de senhas, assim não preciso sempre do PC para pegar uma senha caso precise me logar em algum dos sites usando o celular.

Diferente do `pass`, esse app não possui suporte a plugins o que significa que não posso, através dele, [gerar os tokens MFA que consigo gerar na linha de comando]({{<relref "./19a55b06-mfa-na-linha-de-comando.md">}}) e no [browser](https://github.com/browserpass/browserpass).

Isso significa que, nesses casos onde preciso de um token MFA tenho então que usar um Authentication App, o que torna tudo muito curioso pois agora só preciso do App que gera o token quando estou logando em uma conta **usando o próprio celular**.

O que eu estava acostumado a fazer era sempre pegar o celular quando estava logando em uma conta **usando o PC**. Agora consigo fazer todo o fluxo (desde preencher usuário/senha até preencher o token MFA) usando apenas o PC, o que é de certa forma libertador pois não dependo mais do celular. Inclusive posso eventualmente perdê-lo sem **nenhum prejuízo** para o meu fluxo do dia-a-dia.

Com esses apps que citei acima consigo, no celular: Assinar conteúdos, encriptar, decriptar, autenticar em servidores SSH e ler todas as minhas senhas do meu password manager. Tudo isso usando a chave privada que está dentro do smartcard.


