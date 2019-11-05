---
title: Guia definitivo sobre como guardo minhas senhas e outras informações sensíveis
author: Dalton Barreto
date: 2019-11-05
tags: [yubikey, crypt, gpg, gnupg]
---

# Introdução

Desde que descobri a existência das chaves fabricadas pela [Yubico](https://yubico.com) (Token) fiquei interessado em ter uma para usar como Segundo fator de autenticação ([MFA](https://en.wikipedia.org/wiki/Multi-factor_authentication)), quando descobri que além de segundo fator ela também suportava o uso de chaves GPG fiquei ainda mais curioso para testar um exemplar pessoalmente.

Já escrevi bastante sobre as pesquisas que fiz em relação a isso e esse post é uma tentativa de juntar tudo de uma forma que uma pessoa que acabou de comprar sua chave possa prepará-la para fazer o mesmo uso que eu faço no dia a dia.

Ao longo desse texto irei deixando link para cada um dos artigos que escrevi sobre isso no passado. Se você quiser ver a lista de todos os artigos (inclusive esse), está [aqui](/tags/yubikey).

# Contexto

# Mais do que apenas MFA

O suporte a GPG implementado pelas chaves da Yubico abre muitas novas possibilidades. Desde a possibilidade "óbvia" de poder encriptar/assinar conteúdos digitais até a possibilidade não tão óbvia de poder fazer login SSH usando uma chave que está literalmente sempre no seu bolso.

Nesse post vamos falar basicamente sobre as funções GPG já que a configuração do MFA é bem direta e pode ser encontrada no [próprio site da Yubico](https://www.yubico.com/works-with-yubikey/catalog/#protocol=universal-2nd-factor-\(u2f\)&usecase=all&key=all). Um exemplo é o [Github](https://www.yubico.com/works-with-yubikey/catalog/github/).

# Uso de um password manager

Penso que um password manager deveria ser usado por todos, sem exceção. Guardar todas as nossas senhas em nossa própria memória é um erro que cometemos quase sem perceber e à medida que vamos tendo cada vez mais contas online vamos criando senhas cada vez mais "parecidas" com senhas que já sabemos ou criando senhas "fáceis" de gravar que muitas vezes são também fáceis de adivinhar. E aqui não estou falando de alguém adivinhar sua senha, mas do uso de ataques de [força bruta](https://en.wikipedia.org/wiki/Brute-force_attack) que dependendo da senha da pra rodar em nosso computador pessoal, talvez até em um telefone celular moderno.

## LastPass

O primeiro password Manager que usei foi o LastPass. Isso aconteceu em um dos lugares que trabalhei onde o LastPass era uma das ferramentas do dia a dia. Era usado para compartilhar informações sensíveis.

Nesse momento foi quando eu conheci esse tipo de ferramenta e comecei a adotá-la para guardar minhas próprias informações sensíveis.

O LastPass é bem simples de usar e permite que você tenha acesso aos seus dados usando seu PC ou Celular. Isso foi uma característica que procurei quando estava decidido a trocar de password manager.

## A escolha de um novo password manager

A ideia de trocar de password manager surgiu quando descobri sobre a possibilidade de ter uma chave GPG dentro do token. Poder ter isso significa que eu poderia ter todos os meus dados sensíveis encriptados e ter a certeza de que apenas eu tenho acesso a eles. Mesmo o LastPass prometendo encriptar meu dados, ter a possibilidade de eu mesmo garantir isso pareceu bastante interessante, tanto do ponto de vista de segurança quanto do ponto de vista de pesquisa.

Eu já conhecia GPG há muito tempo mas nunca tinha gostado da ideia de ter minha chave associada (de alguma forma) a um computador ou ter que ter mais de uma chave GPG (uma por PC, por exemplo).

Poder ter a chave GPG dentro de um token físico que eu poderia carregar no bolso pareceu bem atraente.

A partir desse momento comecei a pesquisar sobre outros password managers, mas agora eu tinha uma restrição bem definida: Essa escolha precisava suportar o uso de uma chave GPG para proteger os dados.

Em minhas pesquisas encontrei o `pass`, que é um password manager que usa GPG como feature principal, ou seja, a base de funcionamento gira em torno de uma (ou mais) chave GPG.

# Pass

O [pass](https://www.passwordstore.org/) é uma ferramenta de linha de comando que faz bem apenas uma coisa: Gerenciar dados sensíveis encriptados com uma (ou mais) chave GPG.

Além disso ele ainda permite guardar todos esses dados em um repositório git, afinal o que ele gerencia são apenas arquivos de texto encriptados então podemos salvar esses dados em qualquer lugar e um repositório git é uma ótima ideia.

É claro que você poderia gerenciar esse repositório git de forma independente mas o `pass` já faz um commit automaticamente sempre que você altera qualquer informação. Isso é muito útil pois te dá a segurança de poder "voltar no tempo" se precisar recuperar alguma coisa.

## Features essenciais

Para que a troca do password manager fosse eficiente eu precisaria pelo menos ter as mesmas facilidades (ou o máximo possível) que eu já tinha com a solução anterior. Então quando decidi pelo uso do `pass` já tinha mapeado essas funcionalidades e decidido que elas seriam suficientes para eu deixar de usar a solução anterior.

### Acesso no browser

Apesar do `pass` ser uma ferramenta de linha de comando e isso já me dar a oportunidade de usá-lo quando estivesse no computador mas ter a possibilidade de acessar os dados sem sair do browser era importante pois facilitaria o dia a dia.

Existe uma extensão para do Chrome (roda em outros browsers também) que consegue entender a estrutura e as convenções criadas pelo `pass`.  Essa extensão é a [browserpass](https://github.com/browserpass/browserpass-extension/blob/master/README.md) e pode ser baixada na Chrome web store.

### Acesso no celular

Essa também era uma parte bem relevante das funcionalidades. Não poder acessar minhas senhas pelo celular seria um grande problema. Acho que essa foi a funcionalidade mais difícil de ter rodando de forma satisfatória mas agora que já descobri todos os detalhes a experiência de uso é fantástica.

O app que uso é o  [Password Store](https://play.google.com/store/apps/details?id=com.zeapo.pwdstore) que, assim como a extensão do browser, entende as convenções criadas pelo `pass`. Um bônus desse app é que ele dá suporte ao uso da feature de NFC. O que significa que quando preciso decriptar algum conteúdo basta que eu encoste meu token na parte de trás do celular e tudo funciona.

O Password Store precisa de um segundo App, o [OpenKeyChain](https://play.google.com/store/apps/details?id=org.sufficientlysecure.keychain). Esse é o app que efetivamente fala com a chave da Yubico e fornece uma API para que outros Apps também possam se comunicar com a chave.

# O que você vai precisar

- Um token com suporte a GPG. O token que uso e que mais gostei foi a [Yubico 5 NFC](https://www.yubico.com/product/yubikey-5-nfc). Já usei a [Nano](https://www.yubico.com/product/yubikey-5-nano) também, mas preferi a 5 NFC.
- Um celular com NFC, se quiser usar essa feature. Ou pelo menos um celular com [USB OTG](https://en.m.wikipedia.org/wiki/USB_On-The-Go), que aí você pode plugar a chave na porta USB do celular, usando um adaptador.
- Um PC rodando Linux.

**Observação importante**: Até onde pesquisei o Password Store só existe para Android.

## Gerando sua chave GPG

O primeiro passo é gerar seu "molho de chaves" GPG (keyring GPG). Você pode ter múltiplas chaves e cada uma para um propósito diferente: Encrypt, Sign e Authenticate.

Já escrevi sobre isso antes: [Criando sua keyring GPG de forma fácil](https://daltonmatos.com/2018/10/criando-sua-keyring-gpg-de-forma-facil/).

### Sobre o backup do seu keyring GPG

Uma das coisas mais importantes em relação a tudo que está escrito aqui é: O que fazer se você perder o acesso a todos os tokens físicos que você tem? Como você consegue comprar um token novo e prepará-lo para ser idêntico ao que você perdeu, ou seja, que você continue tendo acesso a todas as suas informações.

É muito importante que você tenha uma (ou mais) cópia desse keyring.

O que eu fiz foi um backup de toda a pasta de dados (`datadir`) do `gnupg` em um `tar.bz2` e guardei "na nuvem"™.

O ideal é guardar essa cópia encriptada, mas como? Afinal, não podemos usar nossa chave GPG para encriptar o backup da própria chave GPG. Se fizermos isso, no momento em que precisarmos acessar esse backup não vamos conseguir, já que só estamos acessando o backup pois perdemos o acesso a todas as outras cópias dessa chave que tínhamos.

O que eu queria também era não ter que decorar uma senha super forte para esse backup, isso porque como não vou acessar esse backup com frequência posso facilmente esquecer essa senha e isso seria catastrófico.

Das opções que pesquisei a que mais gostei foi: Escolha um livro qualquer da literatura mundial e pegue um trecho desse livro como sendo a real senha desse backup. Isso faz com que seja possível escolher uma senha super forte, de tamanho arbitrário (você pode por exemplo escolher um parágrafo inteiro) e não precisamos decorar essa senha, já que agora o que temos que gravar é apenas qual é o livro e qual é o trecho escolhido.

Um detalhe importante é na escolha do livro. O ideal é escolher um livro que você tenha convicção que não será re-editado, por exemplo. Isso diminui as chances de você não conseguir acesso ao livro e acabar perdendo o acesso aos seus dados.

Depois que você escolher qual o trecho do livro, basta usar criptografia simétrica para proteger esse backup.

## Preparando seu novo token para uso

A preparação do primeiro token e de quaisquer outros adicionais que você comprar é igual.

Segue os links para o que já escrevi sobre isso:

[Preparando uma Yubikey 4 Nano para uso diário](https://daltonmatos.com/2018/07/preparando-uma-yubikey-4-nano-para-uso-diario/)

[Comprei uma yubikey nova, e agora?](https://daltonmatos.com/2018/12/comprei-uma-yubikey-nova-e-agora/)

Usei esses mesmos textos para trocar de uma yubikey 4 Nano para uma yubikey 5 NFC.

## Bônus: Usando seu token para guardar sua chave SSH e de assinatura

Uma possibilidade também é poder ter sua chave SSH (Authentication) e de assinatura (Sign) dentro do seu token. Isso significa que você pode, literalmente, carregar sua chave SSH no bolso. Para quem usa múltiplos computadores e tem acesso a múltiplos servidores isso é uma libertação. Antes de poder fazer isso eu tinha uma chave por PC. Agora posso ter apenas uma chave.

Já escrevi sobre isso:

[Usando seu keyring GPG para guardar sua chave SSH](https://daltonmatos.com/2018/08/usando-seu-keyring-gpg-para-guardar-sua-chave-ssh/)

Nesse texto também falo sobre outras chaves que podem ser colocadas dentro do token.

No meu caso guardo também a chave de assinatura digital e assino todos os commits que faço em todos os códigos que produzo, não importando se é código de trabalho, projeto pessoal ou contribuição a projetos de terceiros.

## A importância de se ter um (ou mais) token reserva

Assim como temos o backup de nosso keyring GPG é interessante ter também um token de reserva, ou até mais de um. Isso porque em uma eventual perda do token que você carrega no bolso, você terá um idêntico em casa e poderá retomar suas atividades muito mais rapidamente.

Sempre que tenho uma oportunidade eu compro tokens reserva, mesmo se já tiver algum em casa. Prefiro já estar preparado caso venha a perder algum dos tokens que estão em uso.

# Possibilidades de perder o acesso a todos os meus dados

A pior coisa que poderia acontecer seria eu me "trancar pra fora de casa" e não ter mais acesso aos meus próprios dados. Como estou usando criptografia forte para poder protegê-los tenho que ter a ciência se que se eu mesmo não me cuidar posso ficar sem acesso a tudo e não existiria forma viável de quebrar essa proteção para recuperar esse acesso. Aliás se a quebra dessa proteção fosse viável invalidaria todo o trabalho de pesquisa que fiz para montar um modelo de proteção desses dados.

Escrevi um pouco sobre essas idéias em posts antigos.

[O que acontece se minha Yubikey parar de funcionar?](https://daltonmatos.com/2018/09/o-que-acontece-se-minha-yubikey-parar-de-funcionar/)

[Modelos de segurança para uso de smartcards](https://daltonmatos.com/2018/09/modelos-de-seguranca-para-uso-de-smartcards/)

## Qual o mínimo de acesso que preciso para não perder meus próprios dados?

A única coisa que preciso para garantir que posso ler meus próprios dados que estão encriptados é meu keyring GPG. Apesar de ser apenas "uma coisa" o acesso não é tão simples assim e explico o porque.

Todas as minhas senhas e outros dados sensíveis estão encriptados com essa chave GPG, que atualmente está no token. O problema é que a cópia do keyring está em um local remoto, o arquivo que guarda a senha desse local está em um repositório git, também remoto.

Então se eu perco meu token, não tenho um reserva já preparado e minha cópia da keyring está **apenas** no local remoto eu estou potencialmente travado pra fora. Potencialmente pois ainda existe a chance de passar pelo processo de recuperação de conta para obter acesso a esse backup.

O que faço para mitigar isso é:

- Guardo uma cópia do backup em meu computador pessoal e no computador do trabalho. Ambas encriptadas. Estão lá apenas para um acesso fácil caso eu precise.
- Guardo cópia do repositório git (onde estão todos os dados) no PC pessoal, no PC do trabalho e no celular.
- Mantenho múltiplos token reserva já preparados, idênticos ao que uso atualmente, ou seja, tá com uma cópia de cada chave dentro e protegido pelo mesmo PIN.

Cuidar dos seus próprios dados é conviver com o risco de poder perder esse acesso, afinal só depende de você.

Acredito que com essas cópias e os tokens reservas o risco de perder o acesso a tudo é satisfatoriamente diminuído. Para eu perder acesso a tudo preciso **ao mesmo tempo**:

- Perder meu PC pessoal;
- Perder o acesso ao PC do trabalho;
- Perder meu token principal, que anda comigo;
- Perder todos os tokens reservas já preparados, que ficam guardados;

Se isso tudo realmente acontecer minha última chance é passar pelo processo de recuperação de conta do local onde o backup da minha keyring está armazenado. Se minha chave SSH estiver fora da keyring GPG terei também que passar pelo processo de recuperação de conta do local onde está o repositório git.

Se a chave SSH estiver também no seu keyring GPG, então você já terá acesso ao repositório git assim que tiver acesso ao backup do keyring. Isso significa que você precisará passar pelo processo de recuperação de apenas uma conta.

O primeiro commit do meu repositório git é de 30 de Julho de 2018, isso indica que já estou usando esse modelo há mais de 1 ano. Até hoje perdi um token (e aí usei um reserva) e ainda não errei o PIN mais de 3 vezes, o que bloquearia o token e faria com que eu precisasse de acesso ao backup do keyring.

# Conclusão

Todo esse esforço existe por alguns motivos:

- Não precisar decorar nenhuma senha de nenhum lugar onde eu tenho conta. A única senha que preciso decorar é o PIN que destrava o token, depois disso tudo é decriptado usando o próprio token;
- Poder ter meus dados armazenados de forma verdadeiramente segura, sendo que apenas eu tenho acesso a isso;
- Poder carregar minhas chaves privadas comigo e não depender mais de um PC;
- Aprender mais sobre privacidade e segurança de informações pessoais;

Pensando em um modelo de ataque a esses dados, pra ter acesso a eles uma pessoa precisa:

- De acesso a um token (ou a um dos reservas);
- Ter a senha do token (só 3 chances para acertar);
- Ou ter acesso ao backup do keyring GPG e descobrir a senha de 30 palavras escolhida no momento de encriptar esse backup.

Uso o token diariamente e digito a senha dele múltiplas vezes durante o dia. Isso ajuda muito a gravar de forma mais confiável o PIN que é necessário para destravá-lo.
