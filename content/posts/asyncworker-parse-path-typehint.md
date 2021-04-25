---
title: "Asyncworker: Recebendo parametros do Path do Request através de typehints"
author: Dalton Barreto
date: 2021-04-25
tags: [asyncworker, python, async, http, typehint]
---

No [último post]({{<relref "asyncworker-handler-http-recebendo-mais-do-que-request.md">}}) exploramos algumas possibilidades de um handler http receber mais do que `Request` quando for chamado. Naquele post fizemos uso de um decorator para exemplificar o pasring do body do request.

Nesse post vamos ver o que o asyncworker trouxe de novo para que essa funcionalidade seja mais simples e fácil de usar.

A versão [`0.19.1`](https://github.com/b2wdigital/async-worker/releases/tag/0.19.1) do asyncworker traz um novo typehint que permite receber parametros do path do request: [`PathParam[T]`](https://b2wdigital.github.io/async-worker/userguide/handlers/http/doc.html#handler-path-param).

Esse post usa [`asyncworker==0.19.1`](https://pypi.org/project/async-worker/0.19.1/).

# Ideia geral sobre os typehints inteligentes

O papel principal desses typehints é permitir que os handlers definam em suas assinaturas quais parametros querem receber. A partir dessa assinatura o asyncworker saberá como obter os valores desses parametros e chamará o handler com os valores corretos.

Uma outra característica importante é que o uso desses typehints ajuda também no momento que seu código for checado por um analisador estático, como o [mypy](http://mypy-lang.org/) por exemplo.

Todos os typehints fornecidos pelo asyncwoker são [`Generic[T]`](https://docs.python.org/3/library/typing.html#typing.Generic). Isso significa que se seu handler quiser receber um parametro do tipo `int` ele não vai ser declarado com `(user_id: int)` e sim com `(user_id: PathParam[int])`.

A escolha de se fazer dessa forma foi pra remover ambiguidades. Um handler que recebe (`user_id: int)` poderia receber esse parametro tanto do path quando da query string, por exemplo. Para não termos que escolher ordem de prioridade (no momento do parsing) preferimos ter um tipo específico para dizer **de onde** o valor está vindo.

Outro ponto relevante é que, tendo um tipo intermediário (nesse caso `PathParam`) nos permite fazer lazy parsing do request. O que nos leva ao próximo ponto.



## Extraindo o valor do parametro de dentro do typehint

Como o seu handler recebe `PathParam[int]` temos que ter uma forma de acessar o valor do `int` que foi obtido do request. Essa extração é feita através do método `unpack()`. Todos os typehints fornecidos pelo asyncworker possuem esse método e ele sempre retorna uma instância de `T`, que é o parametro passado ao tipo genérico `PathParam`.

Ter esse método nos permite fazer o efetivo parsing do request apenas quando ele é chamado. Isso é bem útil quando estamos lidando com requests grandes (tamanho em bytes do corpo). Como todos os typehints possuem a mesma interface todos precisam usar a estrutura do `unpack()`.

Esse método é uma corotina, logo deve ser chamado com `await unpack()`. Um exemplo simples de um handler que recebe um `user_id`:

{{<gist daltonmatos 44301ec563ed914ad8fc8bb1d583e15b "handler-recebe-user-id.py">}}

## Regras sobre o uso do typeint PathParam[T]

Existem algumas regras simples para que seja possível usar o typehint `PathParam[T]`.

- O parametro na declaração do path deve ter **o mesmo** nome do parametro na assinatura do handler;
- Qualquer tipo primitivo do python poder ser usado como argumento do `PathParam`: `int`, `float`, `bool`;
    - Quando usar o tipo `bool`, valem as mesmas regras do Pydantic para tipos `bool`: [Pydantic Boolean](https://pydantic-docs.helpmanual.io/usage/types/#booleans).
- Não é permitido usar outros tipos genéricos como parametro do `PathParam`, tais como `List` e `Tuple`. Essa é uma implementação que está no radar mas ainda não está feita;
- Não é permitido usar `Optional[PathParam[T]]`, pelo menos por enquanto.
- Não é permitido usar tipos complexos, por exemplo: `PathParam[User]`.


# Mais exemplos de uso do PathParam[T]

Abaixo vemos outros exemplos de como esse typehint pode ser usado.

## Recebendo múltiplos parametros do path

Podemos receber múltiplos parametros do path, do mesmo tipo ou de tipos diferentes:

{{<gist daltonmatos 44301ec563ed914ad8fc8bb1d583e15b "handler-recebe-multiplos-parametros-do-path.py">}}

Esse handler recebe 4 parametros de tipos diferentes e pode ser chamado dessa forma:

```shell
$ curl -s "http://127.0.0.1:8080/path/on/nome/42/5.93"
{
   "_float" : 5.93,
   "bool" : true,
   "number" : 42,
   "string" : "nome"
}
```

## Ignorando alguns parametros do path

Não é estritamente necessário declarar na assinatura do handler **todos** os parametros que estão na declaração do path. Na assinatura do handler devem estar apenas os parametros que o handler **precisa** receber. Exemplo:

{{<gist daltonmatos 44301ec563ed914ad8fc8bb1d583e15b "handler-ignoring-some-path-params.py">}}

Esse handler funciona normalmente, mesmo não tendo interesse em todos os parametros do path.

```shell
$ curl -s "http://127.0.0.1:8080/path/on/nome/42/5.93"
{
   "bool" : true,
   "string" : "nome"
}
```

## Retornando HTTP 400 Bad Request quando a conversão do valor falha

No caso de um handler querer um `int` mas o request traz uma string, o asyncworker retorna HTTP 400: Bad Request. Por enquanto essa response é `texr/plain` contento apenas o erro original, mas existe a intenção de mudar isso no futuro para poder retornar JSON (ou outro formato preferido).

O mesmo comportamento acontece com os outros tipos, basta que ocorra um erro de validação no valor original. Se o valor original não puder ser convertido para o tipo desejado, retornamos HTTP 400.

{{<gist daltonmatos 44301ec563ed914ad8fc8bb1d583e15b "handler-recebe-user-id.py">}}

Esse handler por exemplo, se receber o seguinte request: `GET /users/abc/books` retornará HTTP 400.

```shell
$ curl -si "http://127.0.0.1:8080/users/abc/books"

HTTP/1.1 400 Bad Request
Content-Type: text/plain; charset=utf-8
Content-Length: 45
Date: Sun, 25 Apr 2021 18:23:45 GMT
Server: Python/3.6 aiohttp/3.7.4

invalid literal for int() with base 10: 'abc'
```

# Futuro

Essa é a primeira implementação de suporte real a typehints inteligentes no asyncworker. É uma implementação funcional e serviu para confirmar que é possível prover funcionalidade através de typehints na assinatura dos handlers. Outras implementções surgirão no futuro, como por exemplo `QueryParam[T]`, `RequestHeader[T]` e `RequestBody[T]`. O objetivo é que seja possível extrair **qualquer parte** do request original para que um handler posssa fazer todo o seu trabalho **sem precisar receber** uma instância de `Request`.

Outras ideias de implementação também envolvem `Optional[PathParam[T]]` e `PathParam[List[T]]`.

Asyncworker é um projeto de código aberto e está hospedado no Github: https://github.com/b2wdigital/async-worker
