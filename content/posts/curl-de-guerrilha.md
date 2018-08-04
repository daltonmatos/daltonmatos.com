---
title: "Curl de Guerrilha"
author: "Dalton Barreto"
date: 2018-08-04 
tags: [curl, cli, linux, commandline]
---

Vou escrever aqui algumas das opções que mais uso no dia a dia quando preciso do comando `curl`. Muitas vezes o curl é usado apenas para "baixar arquivos" e pelo fato dele usar por padrão o `stdout` muitas vezes as pessoas preferem até mesmo usar o `wget`, que por padrão salva o output em um arquivo.

O `curl` é **muito mais** do que um "baixador de arquivos" e diria até que o propósito principal dele nem é esse, apesar dele conseguir fazer isso também.

# curl -i

O `-i` é útil pois ele mostra os headers da resposta que foi recebida. Isso muitas vezes é o que a gente precisa para fazer um debug para conferir o comportamento de algum recurso remoto.

```
$ curl -i https://httpbin.org/ip
HTTP/1.1 200 OK
Connection: keep-alive
Server: gunicorn/19.9.0
Date: Fri, 03 Aug 2018 17:22:53 GMT
Content-Type: application/json
Content-Length: 33
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
Via: 1.1 vegur

{
  "origin": "216.58.202.206"
}
```

# curl -I

O `-I` é semelhante ao `-i` mas com a diferença que o método HTTP usado é `HEAD` em vez de `GET`. Se o servidor funcionar corretamente ele vai responder apenas com os headers, sem um response body. Então essa opção é útil quando queremos ver **apenas** os headers da resposta.

```
$ curl -I https://httpbin.org/ip
HTTP/1.1 200 OK
Connection: keep-alive
Server: gunicorn/19.9.0
Date: Fri, 03 Aug 2018 17:24:56 GMT
Content-Type: application/json
Content-Length: 33
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
Via: 1.1 vegur
```

# curl -H

O `-H` serve para passar headers adicionais no request que será feito. Muito útil para quando você precisa enviar credenciais de autenticação que não são padrão (tipo BasicAuth, etc). Com essa opção você pode enviar qualquer header.

```
$ curl -H "X-Meu-Header: Meu Valor" https://httpbin.org/headers
{
  "headers": {
    "Accept": "*/*",
    "Connection": "close",
    "Host": "httpbin.org",
    "User-Agent": "curl/7.61.0",
    "X-Meu-Header": "Meu Valor"
  }
}
```

A opção `-H` também pode ser usada com a sintaxe `-H@file`, onde `file` é um arquivo ontendo os headers que serão adicionados ao request, muito útil quando são muitos headers e você não quer passar uma opção `-H` para cada header.

# curl -u

Falando em BasicAuth, podemos fazer esse Auth usando a opção `-u`. Quando usamos essa opção podemos fazer de duas formas: `-u <user>` e aí nesse caso o curl vai pedir a senha via `stdin`. Ou `-u <user>:<passwd>` nesse caso já estamos passando o usuário e a senha separados por `:`. Essa última é muito útil se a chamada ao `curl` estiver dentro de um script, por exemplo.

# curl --socks5

O `--socks5` permite usar um proxy como intermediário. Isso é **muito** útil e vou explicar porque. Acho até que é a opção que mais uso no dia a dia.

As máquinas que eu mantenho rodando como parte do meu trabalho estão em uma rede interna, lá no cloud provider que usamos. **Nenhuma** máquina de produção possui IP público, então como conectar (via HTTP/HTTPS, por exemplo) nessas máquinas?

O que fazemos é: Temos apenas **uma** máquina pública, que roda **apenas** SSH e só aceita logins via par de chaves. Esse é o primeiro ponto. Essa máquina pública possui conectividade com as máquinas privadas. Então como usá-la como "ponte" para chegar nas máquinas privadas? `--socks5` com uma ajudinha do seu ssh-client. Aliás SSH é assunto para um posto inteiro.

```
$ ssh -ND 10010 user@host-publico
```

Esse comando liga um Proxy SOCKS5 na porta `10010` da sua interface local, ou seja, `127.0.0.1`.

Agora imagina que existe uma API que responde em `api.myservice` e que esse nome (`api.myservice`) resolve para um IP **privado**, afinal a máquina onde essa API roda só possui esse IP (lembra que nenhuma máquina tem IP público?)

Pois bem, podemos acessá-la assim:

```
$ curl --socks5 127.0.0.1:10010 http://api.myservice
```
E você verá a resposta da API.

Nota: Para isso funcionar desse jeito que mostrei o nome `api.myservice` deve estar em um DNS público. Se esse não for o caso, podemos acessar essa mesma API dessa forma:

```
$ curl --socks5 127.0.0.1:10010 -H "Host: api.myservice" http://10.10.0.45
```
Aqui, assumi que `10.0.0.45` é o IP  do servidor onde a API está rodando ou pelo menos é o IP do Proxy reverso que está na frente dessa API.

# curl --resolve

O `--resolve` é útil quando você precisa usar um nome DNS que ainda não existe ou que você não consegue resolver facilmente (oportuno, não?).

Pegando o exemplo acima e considerando que o DNS não é público, poderemos fazer **o mesmo** acesso assim:

```
$ curl --socks5 127.0.0.1:10010 --resolve api.myservice:80:10.0.0.45 http://api.myservice
```
O que `curl` faz nesse caso é justamente "simular" que esses nomes vieram de um DNS, assim qualquer request para `api.myservice` (porta 80) será feito para `10.0.0.45` como se um DNS tivesse resolvido esse nome pra nós. 

Outra vantagem do `--resolve` é poder ser usados com https. Quando tentamos usar o `-H` para um request HTTPS, vemos isso:

```
dig +short google.com                        
216.58.202.206

curl -H "Host: bla.google.com" https://216.58.202.206                  
curl: (51) SSL: no alternative certificate subject name matches target host name '216.58.202.206'
```

Mas podemos usar o `--resolve` e vemos que não há mais erro de certificado, pois o request foi feito com sucesso e o servidor (nesse caso do Google) respondeu.

```
curl -sI --resolve bla.google.com:443:216.58.202.206 https://bla.google.com
HTTP/2 404 
content-type: text/html; charset=UTF-8
referrer-policy: no-referrer
content-length: 1561
date: Fri, 03 Aug 2018 12:24:28 GMT
alt-svc: quic=":443"; ma=2592000; v="44,43,39,35"
```

# curl -d@-

A opção `-d` serve para passar dados no corpo de um request, geralmente um request POST. A variação `-d@` te permite especificar um arquivo, cujo o conteúdo será o corpo do request. A combinação `-d@-` permite que o `curl` leia esse conteúdo da entrada padrão. Então podemos fazer um request POST usando como corpo do request a saída de um script, por exemplo. Assim:

```
$ meu-script.sh | curl -d@- https://api.myservice/new
```

Usar `-d` implica em trocar o método HTTP para `POST`.

# curl -X

A opção `-X` permite escolher qual será o método HTTP usado. Por exemplo: `-X POST`, `-X DELETE`, `-X PATCH` ou quaisquer outras possibilidades. Só é permitido passar **uma** opção `-X` por chamada do `curl`.

# Outras opções

Existem outras opções também muito úteis mas que ficaram de fora desse post, exemplo: 

* `-L`: Para seguir redirects automaticamente; 
* `-k` para escolher **não validar** o certificado SSL;
* `--connect-timeout`: Para definir um timeout na chamada que o crul fará;

