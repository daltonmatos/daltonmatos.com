---
title: O que acontece se minha Yubikey parar de funcionar?
author: Dalton Barreto
date: 2018-09-20
tags: [yubikey, gpg, pass]
---



Continuando [minha caminhada]({{<relref path="/tags/yubikey">}}) para montar um [modelo de segurança]({{< ref "./modelo-de-seguranca-para-uso-de-uma-yubikey.md">}}) onde consiga guardar meus usuários/senhas de forma segura, surge um ponto bem importante: O que acontece se meu smartcard parar de funcionar de repente?

Vou explicar aqui os procedimentos que seriam necessários para conseguir preparar uma nova Yubikey e voltar ao dia a dia normal.

# Cópia da chave que está no smartcard

Estou assumindo aqui que existe uma cópia da chave que está no smartcard, ok? Caso a chave tenha sido gerada pelo próprio smartcard, não tem muita opção nesse momento a não ser gerar uma chave nova usando o mesmo procedimento. Mas essa opção (o smartcard ter gerado suas chaves) invalida o uso de um password manager como o [pass](https://passwordstore.org), já que todos os dados encriptados com a chave antiga seriam perdidos.

## Múltiplas cópias

Uma coisa que pode te salvar em um momento de desastre é ter múltiplas cópias das coisas que você realmente considera importantes. Nesse nosso caso guardaremos múltiplas cópias da nossa chave GPG (na verdade a cópia é do keyring todo, mas isso é apenas um detalhe).

Duas boas opções são: Guardar uma cópia online e uma "cópia da cópia" offline, no seu PC de uso diário.

### Mantenha uma cópia online

Uma das opções é ter uma cópia online, usando quaisquer serviços que você preferir. Pode ser Dropbox, Google Drive, Amazon S3 ou qualquer outro.

### Cópia guardada no PC

Outra opção é manter uma "cópia da cópia" no PC de uso diário. Lembrando que **qualquer** cópia da chave que esteja fora do smartcard está devidamente encriptada.

# O que fazer em cada um dos casos

A seguir vamos ver qual será o procedimento em caso de perda da Yubikey para cada uma das formas de armazenamento da cópia da chave GPG.

## Recorrendo à cópia que está no PC

Esse é o caso mais simples e fácil pois bastaria decriptar essa cópia e preparar uma nova Yubikey. Easy!

### PC também pára em conjunto com a Yubikey

Mas e se o PC também parar de funcionar?

Aqui estamos em uma situação onde a cópia que estaria no PC está, de alguma forma, inacessível. Nesse caso devemos recorrer à alguma outra cópia.

Esse cenário pode acontecer de algumas maneiras. Uma maneira pouco provável mas possível é você perder o seu PC (HD com defeito ou outra coisa) **ao mesmo tempo** que você perder sua Yubikey. Aqui já conseguimos entender porque não é uma boa ideia manter sua Yubikey sempre inserida na USB do PC.

Uma outra situação poderia ser também a seguinte: O PC estraga e no meio tempo em que você está se preparando para consertá-lo sua Yubikey pára de funcionar.

Nesses dois casos você acaba na mesma situação: PC **e** Yubikey inacessíveis. E aí só te resta uma opção: Acessar a cópia online.

## Recorrendo a uma cópia online para preparar uma nova Yubikey

Aqui temos uma questão interessante. Nós não sabemos a senha do serviço de armazenamento onde a cópia da chave está, afinal todas as nossas senhas ficam em nosso password manager, que por sua vez está totalmente encriptado com a chave que estamos justamente tentando obter!! Sacou o "Lock" em que estamos?


Imagina sua cópia guardada no Dropbox, mas você não sabe a senha do Dropbox afinal sempre que você precisa entrar lá você usa sua Yubikey para decriptar a senhas que estão guardada no seu password manager.

Nesse caso aqui só nos resta uma opção: Passar pelo processo de recuperação de senha do serviço onde nossa cópia está armazenada. Para que isso funcione é importante você ter suas configurações de recuperação de senha (email alternativo e número de telefone) devidamente atualizados, pois quando você precisar isso tem que funcionar!

Mas lembre-se que isso só é necessário se a cópia que fica no seu PC estiver permanentemente inacessível.

Passar pelo processo de recuperação de senha de **uma** conta ainda é melhor do que fazer isso para **todas** as contas. =)

# Passando pelo processo de recuperação de conta

Geralmente para recuperar uma conta você tem duas informações registradas: email alternativo e número de celular. Quando você tem acesso a essas duas informações, a recuperação da conta é imediata. Geralmente um código é enviado para o celular e outro para o email alernativo. Mas e quando você não tem acesso a alguma dessas informações?

Vamos ver agora diferentes "configuraçõe de desastre".

## Yuikey, PC e celular perdidos

Nesse caso são três itens perdidos ao mesmo tempo. Aqui temos duas opções:

1. Usamos os backup codes dessa conta, mas nesse caso temos que ter esses backup codes armazenados de forma segura e **sem** depender da chave GPG;
2. Ficamos sem acesso à conta por alguns dias até ir na operadora de celular e recuperar nosso número, assim basta arrumar um novo telefone e recuperar a conta usando o email alternativo e o celular.

## Yubikey, PC, Celular e e-mail alternativo perdidos

Nesse caso temos 4 itens perdidos ao mesmo tempo. Se a conta de email alternativa tiver as mesmas configurações que temos aqui (senhas gravadas no [pass](https://passwordstore.org/), com a [chave GPG em uma yubikey]({{< ref "./usando-seu-keyring-gpg-para-guardar-sua-chave-ssh.md" >}} ) e [MFA habilitado]({{< ref "./19a55b06-mfa-na-linha-de-comando.md" >}} )) para efetivamente perder o acesso ao email alternativo, a pessoa dona desse email também teria que ter perdido: A yubikey, o PC (que tinha a copia da chave GPG) e o celular. Nesse caso então seriam 6 coisas a serem perdidas ao mesmo tempo: 2 Yubikeys, 2 Celulares e 2 PCs.

Apenas nesse caso mais extremo teríamos que passar pela recuperação de conta onde você precisa comprovar sua identidade e isso geralmente é feito entrando em contato pessoalmente com o provedor da conta que você está tentando recuperar.

Mas acredito que consigo conviver com a probabilidade de 6 coisas serem perdidas simultaneamente para que o acesso à minha conta principal realmente seja perdido. É sempre uma questão de escolha: Até quanto você aceita perder?

Sim, eu já fiz um teste a passei por todo o processo de recuperação de senha do serviço que escolhi, inclusive fiz o teste para caso não tenha mais acesso ao meu celular. Nesse caso parei no ponto onde se eu apertasse um botão, entrariam em contato comigo dentro de 5 dias úteis. Espero nunca ter que usar essa opção. Vamos confiar nas probabilidades. =D

De fato seria bem interessante seu eu pudesse apresentar cópias de documentos pessoais para comprovar que eu sou eu. Assim em um momento de reaver o acesso à conta, bastaria eu ir pessoalmente a algum lugar e apresentar minha carteira de motorista, por exemplo e aí teria novamente acesso à minha conta. Não achei nada a respeito disso, infelizmente.
