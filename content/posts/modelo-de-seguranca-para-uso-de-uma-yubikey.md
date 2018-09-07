---
title: Modelos de segurança para uso de smartcards
author: Dalton Barreto
date: 2018-09-06
tags: [crypt, yubikey, gpg, mfa, 2fa]
---

Desde que descobri a existência de smartcards que podem ser usados como segundo fator de autenticação, fiquei curioso em como seria usar um dispositivo desses no dia a dia.

Minha curiosidade era mais no sentido de quanta "burocracia" um dispositivo desse poderia inserir no meu dia de trabalho.

Na época eu já queria um desses pelo simples fato de ser um token físico, mas pensando bem usar o celular com algum [App](https://authy.com/) de [TOTP](https://en.m.wikipedia.org/wiki/Time-based_One-time_Password_algorithm) seria bem semelhante, talvez até "melhor" já que o App do celular pode exigir uma senha antes de abrir e no caso do token físico, não tem senha nenhuma, basta inserir na porta USB e tocar com o dedo.

Minha atração **definitiva** em relação às keys fabricadas pela [Yubico](https://Yubico.com) foi o fato delas serem PGP Compatibile. Ou seja, não só elas são segundo fator de autenticação mas também podem armazenar de forma segura suas chaves privadas.

Outro ponto que as chaves da Yubico têm é a possibilidade de [armazenar certificados digitais](https://www.yubico.com/solutions/smart-card/), aqueles no formato [x509](https://en.m.wikipedia.org/wiki/X.509). Isso faz ser possível, por exemplo, rodar um site com HTTPS onde a chave privada do certificado está na Yubikey. Um exemplo de experimento sobre isso: [aqui](https://blog.benjojo.co.uk/post/tls-https-server-from-a-yubikey)

**Nota**: Esses certificados também são usados na implementação do Secure Boot, o que me faz pensar que seria possível assinar o GRUB da minha máquina usando uma chave privada que está na minha Yubikey. Dessa forma seria possível fazer a proteção de ponta a ponta usando Secure Boot + [Full disk encryption](/2018/08/arch-linux-com-full-disk-encryption/). Até cheguei a mandar um [tweet para a Yubico](https://twitter.com/daltonmatos/status/1032083641885765634?s=19) sugerindo uma documentação de como fazer isso. Nesse meio tempo, continuo estudando sobre Secure Boot.

# Modelo de segurança para usar uma Yubikey com chaves privadas

Assim que descobri a possibilidade de ter chaves privadas dentro de uma Yubikey comecei a pensar e a pesquisar sobre modelos de segurança para que eu pudesse fazer uso desse novo dispositivo de forma segura (minimamente!) mas ao mesmo tempo sem adicionar muita burocracia no dia a dia e também sem tornar fácil para terceiros terem acesso ao conteúdo das chaves, mas que seja relativamente fácil pra mim.

# Gerando sua chave GPG

O primeiro ponto é como/onde gerar suas chaves. Essa escolha é importante pois você precisa considerar alguns fatores, sendo o mais importante deles: Se sua Yubikey falhar, que alternativas você tem? Você consegue reconstruir uma nova Yubikey com a mesma chave que estava na Yubikey anterior? É aceitável você perder sua chave GPG e simplesmente gerar uma nova, caso tenha que preparar uma nova Yubikey?

Os método escolhido para gerar sua chave depende diretamente desses pontos e de outros quaisquer que fizerem sentido para você.

## Gerando as chaves direto na Yubikey

As [Yubikey da série 4](https://www.yubico.com/yubikey-4-overview/) (possivelmente outras também) possuem uma opção para que o próprio dispositivo gere as chaves pra você. Esse certamente é um jeito **bem seguro** de ter suas chaves, afinal uma vez dentro da Yubikey, sua chave nunca mais sai de lá.

E esse é exatamente um problema também. Pois escolhendo esse modo, no dia em que houver uma falha de hardware na Yubikey **tudo** que tiver sido encriptado usando a chave estará perdido, por exemplo.

Se essa é uma situação que pra você não pode ocorrer, uma outra opção é gerar as chaves por conta própria e depois copiá-las para dentro da sua Yubikey.

## Chaves geradas no PC, como armazenar de forma minimamente segura?

A partir do momento em que as chaves são geradas fora da Yubikey, um novo problema surge: Como guardar essa cópia das chaves de forma segura?

**Nota**: Vamos referenciar essa chave principal como "Master Key" para ficar mais fácil de identificar.

A primeira coisa que vem em mente é guardar essa cópia encriptada, mas que tipo de encriptação usar?

### Guardar a Master Key usando encriptação assimétrica

Para usar criptografia assimétrica seria preciso gerar um novo par de chaves para encriptar a Master Key, mas nesse momento o mesmo problema que estamos tentando resolver surge novamente: Como guardar essa nova chave de forma segura?

E aí entramos em um loop infinito.

### Guardar essa nova chave em um USB stick

Uma opção seria guardar essa nova chave (usada para encriptar a Master Key) em um pendrive. Nesse momento eu tenho mais dois problemas:

1. Onde guardar esse pendrive?
2. E se ele parar de funcionar?

Pesquisando sobre isso vi gente sugerindo guardar em uma safebox no banco, por exemplo. Novamente, o modelo de segurança tem um limite, e esse limite é você quem escolhe. Até onde você aceita perder? Até quanto de vulnerabilidade você aceita ter? Pense nisso.

O problema de depender de um dispositivo físico é que você não sabe quando ele vai parar de funcionar. Imagina você guardar o seu pendrive em um lugar super seguro e na hora que você precisa dele ele simplesmente não funciona.

### Guardando a Master Key usando encriptação simétrica

Uma outra opção é usar encriptação simétrica, nesse caso você precisará escolher e armazenar/memorizar uma senha suficientemente segura (para o seu modelo de segurança).

#### Gerando sua senha usando o método dos dados

Uma forma possível para gerar essa senha é usar o [método dos dados](https://en.m.wikipedia.org/wiki/Diceware), onde você tem um conjunto de X palavras, atribui um número a cada uma delas e vai jogando o dado para escolher essas palavras. Cada palavra requer 5 jogadas do dado. Esses 5 números sorteados no dado são usados para fazer o "lookup" de uma palavra na lista de palavras.

Nesse método você vai precisar armazenar essa senha em algum lugar seguro, afinal memorizar todas as palavras sorteadas é um risco que pouca gente aceita correr.

Lembra do problema de guardar a chave que encripta a Master Key? Aqui estamos na mesma situação. Onde/como guardar essa senha que você acabou de sortear?

Nesse método o tamanho da senha é definido por você. Você escolhe a hora de parar de jogar o dado.

#### Escolhendo sua senha a partir de uma obra literária

Uma outra forma é escolher como senha o trecho de um livro. Nesse método você pode escolher um trecho de uma tamanho razoavelmente grande (2 parágrafos, por exemplo) pois você não precisa memorizar a senha em si, basta lembrar qual o livro e qual o trecho escolhido.

O grande lance aqui é a escolha do livro. Você precisa ter cuidado na escolha da o obra, afinal se você escolher um livro que tem a chance de ser re-editado ou re-escrito de alguma maneira, você pode ter dificuldades de remontar sua senha, já que ela estará vinculada a uma edição específica desse livro.

# Uso da Yubikey no dia a dia

Agora que já temos a chave gerada (e sua cópia guardada de forma segura), precisamos preparar a Yubikey para que ela possa ser usada no dia a dia. Escrevi sobre isso [em um outro post](/2018/07/preparando-uma-yubikey-4-nano-para-uso-diario/).

Eu uso minha chave para 4 propósitos diferentes:

1. Segundo fator de autenticação;
2. Criptografia de dados;
3. Assinatura digital;
4. Autenticação em servidores remotos.

Para usar sua chave basta que ela esteja inserida na porta USB. Na primeira vez que você for usá-la ela te pedirá uma senha para ser destravada. Essa senha pode ser cacheada pelo tempo que você quiser.

Mas se você cachear essa senha por um tempo muito longo, qual a real segurança que essa chave te dá, se ela fica o dia todo já inserida na porta USB do seu PC? Afinal, qualquer pessoa que tiver acesso físico ao seu PC, conseguirá usá-la sem precisar saber a senha.

Essa questão do tempo de cache é um ponto bem importante se você já está com algum nível de paranóia.

Pensando por esse lado, seria melhor você ter que digitar a senha **sempre** que precisar usar a chave, ou então, para diminuir a janela onde um ataque seria possível de acontecer, configurar o cache para um tempo bem curto, como por exemplo 30min ou 1h.

## Paranóia nível hard

O nível de paranóia mais alto provavelmente pertence ao fabricante de um dispositivo desses, pois ele precisa pensar em todos os possíveis ataques que podem ser aplicados a alguém que faz uso dessa chave.

E foi isso que eles provavelmente pensaram quando criaram a funcionalidade de "require touch" nas Yubikeys série 4.

Essas chaves podem ser configuradas para, além de pedir a senha pedir também um toque físico (com o dedo mesmo) para que a operação seja concluída. Esse toque, a partir do momento que é configurado, é pedido **sempre**, não tem "cache".

Mas do que isso te protege? Resposta simples: Ataque remoto.

Imagina o seguinte cenário: Sua chave está inserida na porta USB, você já digitou a senha (e ela está cacheada). Nesse momento, **se por acaso** alguém tiver acesso **remoto** à sua máquina, pode muito bem rodar um comando para decriptar algum conteúdo usando sua chave que está na USB. Como a senha já está cacheada a chave vai, feliz da vida, decriptar o conteúdo e você nem vai desconfiar que ela está fazendo isso.

Agora imagina o mesmo cenário, mas sua chave exige um toque físico antes de completar qualquer ação (encriptação, assinatura, autenticação).

Mesmo que o atacante consiga rodar o comando para decriptar ou assinar um conteúdo, esse comando ficará **parado** aguardando o toque na chave e para esse toque acontecer o atacante deve possui acesso **físico** à sua máquina.

O fabricante ainda vai além. Existem duas formas de configurar esse toque físico: Temporária e definitiva.

Na forma temporária você pode habilitar/desabilitar essa função sempre que quiser, mas na forma definitiva você só pode mudar essa opção se resetar a chave por completo, ou seja, preparar a Yubikey novamente como se fosse nova.

Essas são algumas opções que encontrei durante o tempo que pesquisei para que pudesse fazer uso de uma Yubikey no dia a dia e para um armazenamento seguro de uma cópia das chaves, no caso de precisar refazer uma Yubikey contento o mesmo conjunto de chaves que a Yubikey anterior.

