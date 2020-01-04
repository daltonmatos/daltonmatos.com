---
title: "Asyncworker: Handler HTTP recebendo mais do que Request"
date: 2020-01-04
tags: [python, asyncworker, async, typehint]
---

# Contexto

Uma implementação recente no [asyncworker](https://github.com/B2W-BIT/async-worker) ([doc](https://b2w-bit.github.io/async-worker/userguide/handlers/http.html#handlers-que-recebem-mais-do-que-apenas-request)) permitiu que um handler http pudesse receber parâmetros mais complexos do que simplesmente `Request`, que é o que normalmente um handler http recebe.
Essa implementação permite que possíveis valores possam ser acumulados ao longo da execução do código e no momento que o handler for chamado para atender o `Request` atual, esses valores seriam consultados para saber se o handler está interessado em receber algum deles.
Esse "interesse" é demonstrado pelo handler através da sua própria assinatura python.
O mais legal nesse caso é que tudo isso acaba sendo código python sintaticamente válido. Nesse post usamos o asyncworker `0.11.0`.

Vejamos um exemplo simples.

# Exemplo de um handler HTTP

Quando falamos de framework HTTP geralmente as implementações dos endpoints recebem um objeto `Request` e retornam um objeto `Response`.

## Definição do handler

Vamos escrever um handler http que apenas recebe um JSON no corpo do request e retorna esse json.

O que vamos fazer aqui é escrever código para que nosso handler não precise receber `Request` e possa receber algo mais rico e já validado, como por exemplo um objeto que já represente o corpo do request.

## Handler recebendo Request


{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "handler-recebe-request.py">}}

Aqui temos a implementação padrão do handler, recebendo `Request` e pegando desse request os dados necessários.

## Códigos fornecidos pelo asyncworker para podermos chamar um handler com assinatura dinâmica

O asyncworker fornece uma infra-estrutura de código que ajuda nessa parte de poder ter um handler com a assinatura dinâmica, ou seja, o handler pode ter uma assinatura mais complexa do que um simples `(request: Request)` e podemos inclusive mudar essa assinatura ao longo do tempo sem precisarmos mudar nenhuma linha de código, a não ser a própria linha da assinatura. Veremos exemplos disso mais adiante.

Essa infra-estrutura é dividida em algumas partes:

- `TypesRegistry`;
- Uma instancia de `TypesResgitry` presente em **cada** `Request` que chega;
- A corotina `call_http_handler(request, handler)` que é capaz de analisar a assinatura de uma handler, consultar a instância de `TypesRegistry` que a `Request` possui e chamar o handler com os parametros corretos.

O [TypesRegistry](https://github.com/B2W-BIT/async-worker/blob/d23c8cdf2a29a4560d7017dac2f8a7ef11e9998f/asyncworker/types/registry.py#L4) possui uma interface bem simples para que possamos ir adicionando valores de tipos quaisquer. Tem apenas dois métodos: `set()` e `get()`.

O objeto `Request` original também é modificado e recebe uma instância desse `TypesRegistry`. Isso é feito automaticamente pelo asyncworker, mesmo que você não faça uso dessa estrutura de chamada dinâmica.

A última parte dessa estrutura de código é a função [`call_http_handler()`](https://github.com/B2W-BIT/async-worker/blob/d23c8cdf2a29a4560d7017dac2f8a7ef11e9998f/asyncworker/routes.py#L158-L163). Com ela é possível passar o request original e o handler a ser chamado. Dessa forma o handler terá sua assinatura analisada e será chamado com os parametros corretos.

## Exemplo de decorator que faz uso dessa estrutura para chamar um handler

O que faremos aqui é apenas um decorator "oco", mas que já faz uso dessa estrutura que mencionamos. Do ponto de vista do código do handler nada muda, ele vai continuar recebendo `Request`, mas toda a estrutura para que ele possa receber mais do que isso já estará iniciada.

{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "parse-body-decorator.py">}}

Veja que esse decorator não faz nada demais e o handler continua recebendo o `Request`. Mas podemos começar e modificá-lo para que o handler receba parametros mais ricos.

### Modelo que representa o corpo do request

Vamos definir o modelo que vai representar o corpo do request, que será o `UserResource`. Usaremos [pydantic](https://pydantic-docs.helpmanual.io/) para modelar esse objeto.

{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "user-resource-model.py">}}

É um modelo bem simples e vai ser mesmo apenas para validarmos o que estamos falando, mas lembre-se que esse modelo pode ser arbtitrariamente complexo.

### Modificando nosso decorator para pegar o corpo do request e construir um modelo UserResource


{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "parse-body-decorator-using-user-resource-model.py">}}

A partir de agora nosso request já possui um objeto do tipo `UserResource` dentro do seu `TypesRegistry` e esse objeto já pode ser passado para quaisquer handlers que se interessem por esse tipo. Então podemos mudar a assinatura do nosso handler.

## Mudando a assinatura do handler para receber UserResource

Apenas para relembrar, esse era o código original do nosso handler:

{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "handler-only.py">}}

E esse é o novo código do handler:

{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "handler-recebe-user-resource.py">}}

Aqui temos o handler já recebendo o corpo do request validado. O decorator `parse_body` pode, por exemplo, já retornar `HTTP 400` caso o corpo do request não esteja em conformidade com o modelo `UserResource`. Pode também ser modificado para que fique mais genérico, podendo ser reusado em múltiplos handlers, algo nessa linha:

    @app.route(["/posts"], type=RouteTypes.HTTP, methods=["POST"])
    @parse_body(PostResource)
    async def users(post: PostResource):
      ...

### Versão final do código

Esse é o código em sua forma final, já com o handler usando o decorator e tendo sua assinatura recebendo um modelo já validado:


{{<gist daltonmatos 1bffddc9ca4f36a801cf874b1e37f521 "asyncworker-app-handler-recebe-user-resource.py">}}

## Exemplos adicionais de decorators

Um outro exemplo é um decorator de autenticação que pode fornecer por exemplo um objeto `AuthenticatedUser`. Um handler ficaria com o código nessa linha:

    @app.route(["/users"], type=RouteTypes.HTTP, methods=["POST"])
    @auth
    @parse_body
    async def users(body: UserResource):
        return json_response(body.dict())

O que o decorator `auth` faz é:

- Analisar o request que está sendo atendido;
- Checar se os dados de autenticação estão corretos;
- Buscar os dados do usuário autenticado (ou já retornar `HTTP 401`);
- Adicionar ao `TypesRegsitry` desse request uma instância de `AuthenticatedUser`.

O que isso significa? Significa que esse handler está agora exigindo um request autenticado mas não necessáriamente está interessado em saber **qual** usuário está fazendo o request.

O mais legal é: Se a partir de algum momento o handler quiser saber quem é o usuário autenticado basta mudar a assinatura para:

    async def users(body: UserResource, user: AuthenticatedUser):
        return json_response(user.dict())

Aqui não importa a ordem os parametros, a análise da assinatura será feita da mesma forma e o handler será chamado.

# Futuro

O que vimos aqui é um código ainda experimental e que acabou de ser criado então ainda existem alguns passos que temos que fazer manualmente, como por exemplo a implementação dos decorators mostrados aqui. Fazer com decorators é apenas **uma** forma de fazer.

Podemos por exemplo implementar o decorator `auth` em forma de um middleware, que pode eventualmente ser aplicado a um grupo de handlers.

Um outra ideia também é embutir mais lógica no asyncworker para que cada vez menos decorators/middlewares sejam necessários. Um exemplo simples é o próprio parsing do body do request. Em vez de termos esse decorator `parse_body` o próprio asyncworker poderia fornecer anotações de tipo para isso, assim:

    from asyncworker.types import RequestBody

    @app.route(["/users"], type=RouteTypes.HTTP, methods=["POST"])
    async def users(body: RequestBody[UserResource]):
        return json_response(body.dict())

O mais interessante disso é que parte das regras do sistema (parsing do corpo do request, nesse caso) é descrita com código python válido. Isso significa que não é possível seu código estar escrito de uma forma e se comportar de outra.

Como essas anotações podem ser analisadas dinamicamente podemos, por exemplo, gerar documentaação de forma automática sem que essa documentação fique defasada em relação ao código, afinal é o próprio código quem diz como a documenação será criada.

O que fica aqui são algumas ideias de implementação para o projeto asyncworker. Se você gostou, estamos sempre interessados em receber contribuições para o projeto, tanto código quanto discussão de ideias para o futuro.

O projeto está no github: [https://github.com/B2W-BIT/async-worker](https://github.com/B2W-BIT/async-worker)
