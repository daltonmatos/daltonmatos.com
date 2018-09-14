---
title: TOTP na linha de comando
draft: true
author: Dalton Barreto
tags: [totp, mfa, otp]
---

Acredito que a forma mais comum de MFA atualmente é o uso de "Authenticator Apps". Usei por muito tempo o Google Authenticator até que percebi que, se perdesse meu celular, estaria preso pra fora de todas as contas onde tinha MFA configurado.

Quando percebi isso, descobri o Authy, que faz backup dos seus MFAs pra você e pode sincronizar entre múltiplos dispositivos. Isso já é muito bom, pois você não fica totalmente dependente do celular.

O problema começa quando você precisa recuperar o controle da sua conta Authy. Se você perde o celular sem ter o Authy sincronizado em nenhum outro dispositivo, só resta a você passar por um processo de comprovação de identidade exigido pelo Authy para poder ter novamente em mãos seus tokens MFA (Esse processo pode ser desconsiderado se você mantiver o mesmo número de telefone).

Esse processo, segundo a documentação deles leva alguns dias, o que nem é tão ruim assim considerando que depois disso (e dando tudo certo!) você terá de volta todos os seus tokens e isso significa que não precisará passar pelo processo de recuperação de conta de **todos** os lugares onde você tem MFA habilitado.

Pensando em facilitar minha vida nesse sentido, pensei em eu mesmo ter uma cópia de todos os meus tokens MFA. Minha primeira tentativa foi pedir o meu próprio backup para o suporte do Authy, o que me foi negado.

Comecei então a pesquisar como funcionava o algoritmo que gera os tokens que ficam sendo renovados no Authenticator App, afinal, descobrindo isso poderia gerar esses tokens eu mesmo, até mesmo fora de um app de celular.

# TOTP

Acontece que o protocolo usado pelos apps e obviamente também usados pelas suas contas que requerem MFA é conhecido e pode ser implementado por qualquer um.

O protocolo é o TOTP (Time-Based One Time Password). Como a intenção desse texto não é estudar o algoritmo e si, deixo aqui um link com uma explicação mais detalhada. [TOTP na Wikipédia](links)

# TOTP na linha de comando

Existe um comando já disponível e que implementa esse algoritmo, é o `oathtool`.

O que você precisa para usá-lo é a chave privada gerada pelo seu provider, ou seja, o provedor da conta onde você está habilitando MFA.

Já reparou que, além do QRcode que geralmente é mostrado, sempre tem um link dizendo algo nessa linha: "Não consegue scanear o código acima?” ou, "Digite manualmente", etc.

Veja um exemplo:

Colocar imagem do AWS, mostrando o valor da chave privada.

Esse é o link que vai te dar o **conteúdo** da chave privada que está codificada no QRcode. De posse desse conteúdo, basta passá-lo para o `oathtool`, assim:

**Nota**: No exemplo estou usando uma [variável de ambiente encriptada](link) contendo o valor da chave privada, isso para evitar que a chave privada fique no histórico do meu shell. Depois vamos guardá-la no password manager.

```
$ oathtool <key>
```

Dessa forma ele vai gerar **exatamente** os mesmos tokens que o celular geraria, caso tivesse escaneado o QRcode correspondente.

# Plugin OTP para o pass

Minha [migração do LastPass para o pass](link) ficou ainda melhor quando descobri que existe um plugin para o `pass` que é capaz de gerar esses tokens MFA.

O que precisamos fazer é apenas ter em mãos a chave privada de cada um dos MFAs e passar isso para o plugin, dessa forma:

```
$ pass otp append -s -i <provider> <pass-name>

```
Onde `<provider>` é um identificador **qualquer** apenas para te dizer de qual conte é esse MFA e `<pass-name>` é uma entrada no seu [password-store](so long LastPass)
A partir desse ponto podemos fazer isso:

```
$ pass otp social/twitter.com/daltonmatos
645398
```
E ele vai gerar um token MFA **válido** pra nós. 

# Registrando esse mesmo MFA no celular

Se você preferir ou até mesmo quiser esse esse MFA no PC **e** no celular, basta re-gerar o qrcode original, usando esse mesmo plugin do `pass`, assim:

```
$ pass otp uri -q <pass-name>
```

Onde `<pass-name>` é a entrada onde o MFA está gravado. Um exemplo:

```
$ pass otp uri -q social/twitter.com/daltonmatos

```

Essa é uma forma de você ter **total** controle de todos os seus tokens MFA. Tendo as chaves privadas de cada um deles, não importa mais se você perdeu o celular ou não, pois você não depende mais **exclusivamente** do celular para gerar os tokens.

Mas também cabe a você guardar esses tokens de forma segura.
