---
title: SSH de Guerrilha
author: Dalton Barreto
date: 2018-08-26
tags: [ssh, linux, cli, terminal]
---


Boa parte do meu dia envolve usar `ssh`. Às vezes como comando direto para fazer acesso remoto a algum servidor e às vezes como ferramenta para poder executar alguma outra tarefa.

Nesse texto vamos ver os usos mais comuns que faço desse comando e algumas configurações que fui acumulando ao longo do tempo.

# SSH Config

O primeiro ponto que temos que ter bastante atenção é o arquivo de configuração. Muita gente acha que apenas o `ssh-server` possui um config, mas isso não é verdade. O `ssh-client` (ou apenas `ssh`) também possui e perdemos a chance de melhorar muito seu uso quando deixamos de usar um config.

## Server alias

O primeiro ponto que o config traz é a possibilidade de dar apelidos para servidores que você acessa com frequência.

A configuração mais simples que você pode fazer é essa:

```
Host meu-host
Hostname 10.234.3.26
```

A diretiva `Host` nos permite criar o alias. E a diretiva `Hostname` é o endereço real do servidor para o qual estamos criando esse alias.

A partir de agora você pode fazer:

```
$ ssh meu-host
```

Sempre que quiser acessar esse servidor. E tem um bônus, seu shell provavelmente **auto completa** esses alias, o que é uma mão a roda.

**Nota**: a cada linha encontrada do arquivo de configuração e que começa pela palavra `Host` significa um novo bloco de configurações. Esse bloco pode ser relacionado a um servidor (como acabamos de ver) ou a vários servidores (veremos isso já já).

## Configuração para múltiplos servidores

Uma coisa que descobri depois de muito tempo usando SSH é que a diretiva `Host` permite o uso de wildcards, ou seja, posso criar um bloco de configuração que se aplica a múltiplos servidores, até mesmo servidores que não estão explicitamente configurados!

Um exemplo simples: Imagina que temos um config que usamos tanto em nossa máquina pessoal quanto na máquina do trabalho. Podemos então fazer o seguinte:

**Nota**: Não se importe, por enquanto, com diretivas novas nesse config de exemplo, veremos todas elas no detalhe mais adiante.

```
Host work.*
User usuario-do-trabalho
IdentityFile ~/.ssh/chave-do-trabalho

Host work.webserver
Hostname web.host.com.br

Host work.db
Hostname db.host.com.br

Host personal.app
Hostname myhost.com.br
User otheruser
IdentityFile ~/.ssh/otherkey
```

Nesse caso, sempre que fizermos `ssh` para um alias que comece com `work.` as configurações do bloco `work.*` serão aplicadas. Veja:

```
$ ssh -v work.db
OpenSSH_7.7p1, OpenSSL 1.1.0h  27 Mar 2018
debug1: Reading configuration data /home/daltonmatos/.ssh/config
debug1: /home/daltonmatos/.ssh/config line 1: Applying options for work.*
debug1: /home/daltonmatos/.ssh/config line 8: Applying options for work.db
debug1: Connecting to db.host.com.br [<IP>] port 22.
debug1: Connection established.
...
...
debug1: Authenticating to db.host.com.br:22 as 'usuario-do-trabalho'
```

Perceba as linhas:

```
debug1: /home/daltonmatos/.ssh/config line 1: Applying options for work.*
debug1: /home/daltonmatos/.ssh/config line 8: Applying options for work.db
```

Isso nos mostra que as duas configurações (`work.*` e `work.db`) foram aplicadas. Esse acesso que acabamos de fazer é equivalente a essa linha de comando (caso não tivéssemos nosso config)

```
$ ssh -i ~/.ssh/chave-do-trabalho usuario-do-trabalho@db.host.com.br
```

Bem melhor a versão com config né? E ainda tem auto-complete.


## Configuração wildcard para hosts dinâmicos

Existe uma forma de se aplicar configurações wildcard para hosts que nem estão no config.

Apesar da diretiva `Host` designar um alias, podemos usar parte de um IP nessa diretiva, assim:

```
Host 10.235.*
User user
Port 22
```

Perceba que nem temos a diretiva `Hostname` e isso não é um problema. A partir de agora, sempre que acessarmos um servidor cujo "apelido" comece com `10.235` essas configurações serão aplicadas.

Então, no fim das contas, qualquer servidor que possua seu IP começado por `10.235` entra nessa lista, veja:

```
$ ssh -v 10.235.10.44
OpenSSH_7.7p1, OpenSSL 1.1.0h  27 Mar 2018
debug1: Reading configuration data /home/daltonmatos/.ssh/config
debug1: /home/daltonmatos/.ssh/config line 16: Applying options for 10.235.*
debug1: Connecting to 10.235.10.44 [10.235.10.44] port 22.
debug1: Connection established.
```

Veja que o `ssh` aplicou todas as configurações de `Host 10.235.*` quando fizemos esse acesso, mesmo não existindo um bloco de configuração `Host 10.235.10.44`.

Usar o IP como alias é útil quando você não quer configurar uma centena de máquinas manualmente no seu config e para isso coloca ali só parte do IP e assim consegue acessar todas elas sem precisar ficar mexendo no seu config toda hora.

# Outras opções interessantes para usar no Config

Existem outras opções que podemos colocar em um bloco de configuração.
Aqui vamos ver algumas, mas nem de longe isso vai cobrir todas as opções possíveis.

Uma lista completa você consegue encontrar no manual do `ssh_config` (`man ssh_config`)


## User, Port, IdentityFile

No exemplo que acabamos de ver dissemos apenas qual o IP (ou DNS) do servidor. Mas podemos por exemplo escolher o usuário, porta e qual chave deverá ser usada.

```
Host meu-host
Hostname 10.234.3.26
User meu-user
Port 22
IdentityKey ~/.ssh/minha-chave
```

Nesse caso, mesmo que nosso usuário local seja `outrouser`, quando digitarmos `ssh meu-host` vamos usar `meu-user` como usuário de conexão. A porta usada será a `22` e a chave privada será o arquivo `~/.ssh/minha-chave`.

## ProxyCommand

Essa opção é extremamente útil quando você precisa usar uma máquina como "ponte" para chegar em outra.

Por muito tempo eu copiei minha chave privada para essa "máquina ponte" para depois, de lá, fazer o ssh para a máquina destino. Pensando nisso, hoje, que tenho minha chave privada [guardada em um dispositivo físico](/2018/08/usando-seu-keyring-gpg-para-guardar-sua-chave-ssh/#usando-sua-yubikey-como-chave-privada-ssh), seria inviável fazer essa cópia, ou se na pior das hipóteses eu resolvesse realmente copiar a chave privada, usar um token físico para guardá-la perderia totalmente o sentido.

Pensa em uma infra estrutura que está em algum cloud provider e que todas as máquinas são privadas, ou seja, **não possuem** IP público. Como acessar essas máquina via ssh?

Entra o `ProxyCommand`, com ele conseguimos pedir ao ssh que faça o acesso remoto com a ajuda de um comando intermediário.

Vamos ao exemplo:

Temos duas máquinas, uma privada com IP `10.235.44.69` e uma com IP público, que pode ser acessada pelo nome `public.server.com.br`. Essa máquina com IP público serve **apenas** como ponte, ou seja, não roda **nada** a não ser `ssh-server`.

Com o comando abaixo conseguimos chegar na máquina privada, **sem** copiar nossa chave privada pra lugar nenhum e sem precisar expor a máquina privada para internet.

```
$ ssh -o "ProxyCommand=ssh public.server.com.br -W %h:%p" `10.235.44.69`
```

Podemos fazer a mesma coisa no arquivo de configuração, assim:

```
Host 10.235.*
ProxyCommand ssh public -W %h:%p

Host public
Hostname public.server.com.br
```

Agora podemos fazer apenas `ssh 10.235.44.69` e conseguiremos o mesmo acesso.

Você pode também encadear quantos "saltos" você quiser. Cada bloco de configuração (`Host`) pode ter seu próprio `ProxyCommand`.

Como exemplo, para eu acessar minha estação de trabalho eu faço 2 "saltos". O caminho é mais ou menos esse: Minha casa -> AWS -> Datacenter on-premise -> Minha estação de trabalho.

Isso funciona porque a máquina da aws é pública, essa conta da aws tem VPN com o datacenter on-premise e esse datacenter tem VPN com o escritório. Tudo isso é feito com `ProxyCommand` e ainda assim digito apenas `ssh minha-maquina` para cair já dentro da minha estação de trabalho.

## LocalForward ou -L

O `LocalForward` é útil quando você quer se conectar a alguma porta de uma máquina remota, novamente estamos falando de máquinas privadas que nem sequer possuem IP público.

```
Host myhost
Hostname 10.234.33.77
LocalForward 3306 127.0.0.1:3306
```

**Nota**: Aqui estamos assumindo que as configurações de `ProxyCommand` (caso necessárias) já estão feitas.

Usando esse config, quando acessamos `ssh myhost` uma porta (`3306`) é aberta em nossa máquina local e **todo o tráfego** que chegar nessa porta é automaticamente redirecionado para a porta remota no endereço `127.0.0.1:3306`. Como nesse caso colocamos o destino como `127.0.0.1` significa que estamos querendo uma porta no host de destino.

Mas isso não é uma restrição, ou seja, podemos nos conectar no host `A` mas fazer o `LocalForward` para um host `B`. Para isso basta que o host `A` tenha conectividade **direta** com o host `B`. E você precisa ter acesso `ssh` ao host `A` para que consiga fazer esse `LocalForward`. Sua conexão com o Host `A` pode passar por quantas "máquinas-ponte" você quiser, não há restrições nesse sentido.

Então podemos fazer isso:

```
Host myhost
Hostname 10.235.20.66
ProxyCommand ssh other-host -W %h:%p
LocalForward 3306 10.40.5.88:3306
```

Nesse caso estamos nos conectando ao host `myhost`, usando uma máquina como "ponte" (`other-host`, que pode inclusive estar usando outras máquinas-ponte pelo caminho) e estamos querendo nos conectar na porta `3306` de um terceiro servidor, `10.40.5.88`.

Com esse acesso feito, se você se conectar na porta `localhost:3306` você estará, na verdade, se conectando na porta `3306` do host `10.40.5.88` que está em alguma rede **privada** em algum lugar do mundo.

Veja um exemplo:

```
$ ssh myhost
...
...
...
Authenticated to 10.235.20.66 (via proxy).
debug1: Local connections to LOCALHOST:3306 forwarded to remote address 127.0.0.1:3306
debug1: Local forwarding listening on ::1 port 3306.
debug1: channel 0: new [port listener]
debug1: Local forwarding listening on 127.0.0.1 port 3306.
```

Esse trecho acima indica que o redirecionamento da porta está feito.

A sintaxe dessa diretiva é: `LocalForward [bind_address]:port host:hostport`. Se `bind_address` for omitido, será usado `127.0.0.1`. Podemos também usar `*` no parâmetro `bind_address`, nesse caso todas as interfcaes locais estarão com a porta aberta.


Essa funcionalidade também está disponível como uma command line flag, `-L`. A sintaxe é quase a mesma. A diferença é que em vez se separar os argumentos por espaço, separamos com `:`, assim: `-L 127.0.0.1:3306:127.0.0.1:3306`.

## DynamicForward ou -D

O `DynamicForward` é uma opção especialmente útil quando queremos acessar portas de servidores remotos mas sem precisar nos preocupar em ficar criando redirecionamentos (`-L`).

O que essa opção faz é ligar localmente um Proxy `SOCKS5` que usa a conexão SSH como "meio de transporte".

Vamos pegar o mesmo cenário de antes, um servidor privado com alguns sistemas rodando, por exemplo uma app `HTTP` rodando nas portas `80` e `8080`. O que podemos fazer é acessar uma máquina que tenha conectividade com essa (onde está rodando a app) e usar um Proxy `SOCKS5` para "tunelar" nosso acesso até a máquina destino, vejamos o config:

```
Host meu-server
Hostname 10.244.40.66
DynamicForward 127.0.0.1:10010
```

E assim fazemos o acesso, normalmente:

```
$ ssh -v meu-server
...
...
debug1: Local connections to 127.0.0.1:10010 forwarded to remote address socks:0
debug1: Local forwarding listening on 127.0.0.1 port 10010.
```
Essa é a parte importante do output, onde ele confirma que o redirecionamento está sendo feito.

Nesse momento, pelo tempo que essa sessão SSH ficar ativa, a porta `10010` estará aberta em nossa máquina local (`127.0.0.1`) e podemos usar essa porta como Proxy. 

Um exemplo de acesso a uma app, na porta 80 em um servidor **privado**, usando esse proxy seria assim (usando [curl](/2018/08/curl-de-guerrilha/)):

```
$ curl --socks5 127.0.0.1:10010 http://10.234.55.89/healthcheck
```

Sendo `10.234.55.89` um servidor **qualquer** que possui conectividade direta com o `meu-server` (`10.244.40.66`).

O que está acontecendo aqui é que apesar de estarmos rodando o `curl` localmente, quem faz o acesso real à app é o `meu-server`, afinal o `curl` está usando um Proxy para fazer o acesso por ele.

Todos os browsers modernos possuem opções para usar um Proxy `SOCKS5`, então essa opção torna-se especialmente útil por outro motivo: Poder burlar regras de saída de firewalls.

Se você está em um ambiente controlado (não por você) e essa rede impõe limites de acesso, essa opção pode ser útil para driblar esses limites. Para isso basta que essa rede permita acesso remoto via SSH. Se isso estiver permitido, basta tunelar todo o seu tráfego e você poderá acessar **qualquer** destino, mesmo os explicitamente bloqueados pela rede onde você está.

Mesmo se a rede bloquear a porta `22` (padrão do SSH) ainda pode existir uma saída: Rodar SSH na porta `443`. A porta `443` é a padrão para HTTPS e *geralmente* essa porta é liberada mesmo em ambientes **bem** controlados.

## ForwardAgent ou -A

Essa opção é útil para que possamos fazer `ssh` a partir da máquina remota, mas usando as mesmas credenciais locais. Imagina você se logando em um server remoto e a partir dessa máquina fazendo um `git pull` (ou `git clone`) de um repositório privado. Veja um exemplo:

```
$ ssh meu-host
daltonmatos@meu-host $> ssh git@github.com
Warning: Permanently added the RSA host key for IP address '192.30.253.112' to the list of known hosts.
Permission denied (publickey).
```

Agora com `-A` (ou com `ForwardAgent` no arquivo de config)

```
$ ssh -A meu-host
daltonmatos@meu-host $> ssh git@github.com                          
PTY allocation request failed on channel 0
Hi daltonmatos! You've successfully authenticated, but GitHub does not provide shell access.
Connection to github.com closed.
```

Na segunda sessão, consegui fazer uma autenticação com sucesso, mas usando minhas credenciais locais, sem precisar copiar nenhuma chave para lugaar nenhum.

Se usado no config essa diretiva recebe apenas um parâmetro, `yes` ou `no`, assim:

```
Host meu-host
Hostname 10.234.55.69
ForwardAgent yes
```

## -N

A opção `-N` é útil quando você quer dar a oportunidade de alguém conectar em um servidor via SSH, mas ao mesmo tempo não quer que essa pessoa tenha acesso ao Shell desse servidor, ou seja, que não seja possível para essa pessoa rodar comandos arbitrários, mas que ainda assim ela possa usar as outras opções mostradas aqui, como Proxy (`-D`) e redirecionamento de porta (`-L`).

Útil quando você não quer dar shell no server remoto mas mesmo assim quer permitir Port forwarding.


# Adicionando redirecionamento de portas depois da conexão já estar feita

Muita vezes iniciamos a sessão `ssh` e só depois lembramos que deveríamos ter chamado o comando `ssh` (lá no host de origem) com algum redirecionamento de portas ativado.

Passei muito tempo fechando a conexão `ssh` atual só para poder pegar o comando no histórico e adicionar as opções que estavam faltando.

Mas existe uma forma de fazer isso **sem se desconectar** do host remoto.

Para isso precisamos acessar um shell interno do `ssh`. Temos que estar com o buffer do terminal limpo, sempre dou alguns Enters para "garantir" isso.

Para entrar nesse Shell interno digite `~<space>C`. Isso mesmo: "til+espaço+C maiúsculo". Isso deve mostrar um novo prompt, assim: `ssh>`

Se estamos em uma conexão remota e queremos ligar o proxy `SOCKS5`, podemos fazer:

```
$ ssh meu-server
...
...
daltonmatos@meu-server $>
daltonmatos@meu-server $>
daltonmatos@meu-server $>
 
ssh> -D 10010
Forwarding port.
```


A partir de agora esta conexão SSH está funcinando como se tivesse sido chamada, desde o início, com `ssh -D 10010 meu-server`.

Essas são as opções disponíveis nesse shell interno:

```
ssh> help
Commands:
      -L[bind_address:]port:host:hostport    Request local forward
      -R[bind_address:]port:host:hostport    Request remote forward
      -D[bind_address:]port                  Request dynamic forward
      -KL[bind_address:]port                 Cancel local forward
      -KR[bind_address:]port                 Cancel remote forward
      -KD[bind_address:]port                 Cancel dynamic forward
```

## Desconectado uma sessão "congelada"

Muitas vezes nos vemos com um terminal congelado porque uma sessão SSH está presa, seja por algum problema remoto ou porque a conexão caiu mesmo. Nesse caso, em vez de fecharmos o terminal inteiro (fiz isso por muito tempo) podemos acessar esse mesmo "shel interno", mas agora em vez de usar `C` (C maiúsculo) vamos usar ponto, assim: `~<space>.`

```
daltonmatos@meu-server $>
daltonmatos@meu-server $>
daltonmatos@meu-server $>
Connection to 10.234.55.68 closed.
```

# Shell alias para facilitar o acesso (e cópia de arquivos) a máquinas privadas

Preciso tanto usar `ssh` com máquinas privadas que escrevi algumas funções e criei alguns alias que facilitam minha vida. Em vez de precisar configurar toda e qualquer máquina privada que faço acesso e de ficar adicionando configurações de `ProxyCommand` para cada novo servidor uso um alias que criei chamado `ssh-via`. Com esse alias posso escolher qual máquina vou usar como ponte e a sintaxe é: `ssh-via <ponte> <maquina-destino>`.

Então posso ter um servidor, por exmeplo, `private-server`. Quero usar esse servidor como ponte para chegar em outro, ou melhor, quero usá-lo para poder chegar uma série de máquinas, pertencentes a uma mesma rede. Então posso fazer isso:

```
$ ssh-via private-server other-server
```

Quaisquer opções de linha de comando podem ser passadas normalmente, basta que sejam passadas **após** o argumento que define a máquina-ponte, assim:

```
$ ssh-via private-server -D 10010 -L 3306:127.0.0.1:3306 other-server
```

## SCP

Fiz o mesmo para conseguir copiar arquivos **direto** da minha máquna local para uma máquina remota (e **privada**!) e também para fazer o contrário, ou seja, copiar dados do servidor remoto para minha máquina local. Esse alias é o `scp-via`. Funciona do mesmo jeito do `scp` normal, mas recebe como primeiro parametro o máquina-ponte, assim:

```
$ scp-via private-server /tmp/file other-server:/tmp/file
```

Novamente, podemos passar quaisquer opções que o `scp` aceite, basta que seja **após** o parametro que define a máquina ponte:

```
$ scp-via private-server -C /tmp/file other-server:/tmp/file
```

O código dessas duas funções está abaixo, e está também em meu [dotfiles](https://github.com/daltonmatos/dotfiles/blob/master/zsh/zshrc#L181-L194).


{{<highlight zsh>}}
_ssx_via(){
  COMMAND=${1}
  gateway=${2}
  shift; shift
  $COMMAND -o "ProxyCommand=ssh ${gateway} -W %h:%p" -o "StrictHostKeyChecking=no" $*
}

_ssh_via(){
  _ssx_via 'ssh' $*
}

_scp_via(){
  _ssx_via 'scp' $*
}

{{</highlight>}}
