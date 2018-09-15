---
title: Multi Factor Authentication na linha de comando
date: 2018-09-15
author: Dalton Barreto
tags: [totp, mfa, otp, pass, 2fa]
---

Acredito que a forma mais comum de MFA atualmente é o uso de "Authenticator Apps". Usei por muito tempo o Google Authenticator até que percebi que, se perdesse meu celular, estaria preso pra fora de todas as contas onde tinha MFA configurado.

Quando percebi isso, descobri o [Authy](https://authy.com/), que faz backup dos seus MFAs pra você e pode sincronizar entre múltiplos dispositivos. Isso já é muito bom, pois você não fica totalmente dependente do celular.

O problema começa quando você precisa recuperar o controle da sua conta Authy. Se você perde o celular sem ter o Authy sincronizado em nenhum outro dispositivo, só resta a você passar por um processo de comprovação de identidade exigido pelo Authy para poder ter novamente em mãos seus tokens MFA (Esse processo pode ser desconsiderado se você mantiver o mesmo número de telefone).

Esse processo, segundo a documentação deles, leva alguns dias. Isso nem é tão ruim assim considerando que depois disso (e dando tudo certo!) você terá de volta todos os seus tokens e isso significa que não precisará passar pelo processo de recuperação de conta de **todos** os lugares onde você tem MFA habilitado.

Pensando em facilitar minha vida nesse sentido, pensei em eu mesmo ter uma cópia de todos os meus tokens MFA. Minha primeira tentativa foi pedir o meu próprio backup para o suporte do Authy, o que me foi negado.

A opção que restou então foi re-gerar todos os meus MFAs e desa vez, guardar uma cópia de cada um deles.

Já que vou tê-los nas mãos, comecei então a pesquisar como funcionava o algoritmo que gera os tokens que ficam sendo renovados no Authenticator App, afinal, descobrindo isso poderia gerar esses tokens eu mesmo, até mesmo fora de um app de celular.

# O Protocolo

Acontece que o protocolo usado pelos apps e obviamente também usados pelas suas contas que requerem MFA é conhecido e pode ser implementado por qualquer um.

O protocolo é o TOTP (Time-Based One Time Password). Como a intenção desse texto não é estudar o algoritmo e si, deixo aqui um link com uma explicação mais detalhada. [TOTP na Wikipédia](https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm)

# TOTP na linha de comando

Existe um comando já disponível e que implementa esse algoritmo, é o `oathtool`.

O que você precisa para usá-lo é a chave privada gerada pelo seu provider, ou seja, o provedor da conta onde você está habilitando MFA.

Já reparou que, além do QRcode que geralmente é mostrado, sempre tem um link dizendo algo nessa linha: "Não consegue scanear o código acima?” ou, "Digite manualmente", etc.

Esse é o link que vai te dar o **conteúdo** da chave privada que está codificada no QRcode. De posse desse conteúdo, basta passá-lo para o `oathtool`:

**Nota**: Acabei de descobrir que o Mercado Livre não permite que você veja essa informação. Eles, de alguma forma, mandam os dados direto pro aplicativo, no caso deles é o Authy.

Veja um exemplo de como é na AWS, no momento em que você está ativando MFA para uma conta qualquer:

[![Ativação de MFA na AWS](/static/19a55b06/mfa-aws.png)](/static/19a55b06/mfa-aws.png)

Nesse caso, a chave é `YOPZKAL6OQSQM6FTM6TI4OHHDIWUOS5U5IAP7OEQZTGMPMFDFT7JT6RR4R4HEE2J`. É esse valor que precisamos passar para a ferramenta e é ele que vamos usar de exemplo nesse texto.


```
$ oathtool -b YOPZKAL6OQSQM6FTM6TI4OHHDIWUOS5U5IAP7OEQZTGMPMFDFT7JT6RR4R4HEE2J
038301
```

Dessa forma ele vai gerar **exatamente** os mesmos tokens que o celular geraria, caso tivesse escaneado o QRcode correspondente.

A partir de agora podemos gerar nossos tokens na linha de comando, sempre que formos perguntados pelo segundo fator, no momento do login.

**Nota**: Já tentou scanear esse QRcode sem usar o aplicativo de Autenticação? Dá uma olhada e vai ver que a chave privada está lá, em algum lugar.

# Plugin OTP para o pass

Minha [migração do LastPass para o pass]({{<relref "./so-long-lastpass-and-thank-you-for-all-the-fish.md">}}) ficou ainda melhor quando descobri que existe um plugin para o `pass` que é capaz de gerar esses tokens MFA.

O que precisamos fazer é apenas ter em mãos a chave privada de cada um dos MFAs e passar isso para o plugin, dessa forma:

```
$ pass otp append -s -i <provider> <pass-name>
```

Onde `<provider>` é um identificador **qualquer** apenas para te dizer de qual conta é esse MFA e `<pass-name>` é uma entrada no seu [password-store](https://www.passwordstore.org/).
A partir desse ponto podemos fazer isso:

```
$ pass otp <pass-name>
645398
```

E ele vai gerar um token MFA **válido** pra nós referente ao MFA da entrada `<pass-name>`. 

# Registrando esse mesmo MFA no celular

Se você preferir ou até mesmo quiser esse esse MFA no PC **e** no celular, basta re-gerar o qrcode original, usando esse mesmo plugin do `pass`, assim:

```
$ pass otp uri -q <pass-name>
```

Onde `<pass-name>` é a entrada onde o MFA está gravado. Nesse momento o `pass` vai te mostrar um QRcode que você pode escanear no celular e usar normalmente.

Essa é uma forma de você ter **total** controle de todos os seus tokens MFA. Tendo as chaves privadas de cada um deles, não importa mais se você perdeu o celular ou não, pois você não depende mais **exclusivamente** do celular para gerar os tokens.

Mas também cabe a você guardar esses tokens de forma segura.
