---
title: "Chamando funções Python com assinatura dinâmica Baseada em Typehint"
date: 2020-01-03
tags: [python, typehint]
---

# Contexto

Com a possibilidade de declarar tipos em códigos python vem uma possibilidade interessante: Poder deduzir quais parâmetros uma função (ou método) quer receber e fazer essa chamada dinamicamente.

Isso te dá a possibilidade de eventualmente mudar a assinatura de um método e ainda assim não mudar a chamada a esse método, isso porque os parâmetros são "resolvidos" no momento da chamada e não mais no momento da escrita do código.

# Um pouco sobre typehint

Typehint é uma forma de "anotar" tipos relacionados ao seu código python. Essa possibilidade sugriu no python na [PEP-484](https://www.python.org/dev/peps/pep-0484/) e pode ser usada inclusive para fazer análise estática de tipos no seu código, mas isso é assunto para outro post.

O typehint, como o próprio nome diz, é apenas uma "dica" de qual é o tipo de cada parâmetro de seu código. Cabe a você honrar esses tipos e obedecer essas anotações.

Essa ideia de descobrir dinamicamente o valor a ser passado em uma chamada a uma função python é totalmente baseado na declaração de tipos que está no código. Isso significa que estamos assumindo que os tipos estão sendo obedecidos.

Uma ótima forma de fazer o enforcement desses tipos no seu código é usando um analisador estático como o [mypy](http://mypy-lang.org/).

## Analisando a assinatura de uma função dinamicamente

O início de tudo é ter os parâmetros dessa função com seus tipos declarados. Caso contrário não teremos como inferir quais valores são possíveis de serem passados.

Uma declaração simples pode ser:

```python
  async def func(a: int, b: str) -> int:
    pass
```


É possível, via introspecção, descobrir quais são os tipos que estão declarados nesses typehints. Uma forma simples é olhando o atributo `__annotations__` que toda função (e métodos) possui. Olhando esse caso temos:

```python
  print(func.__annotations__)
  {
  'a': <class 'int'>,
  'b': <class 'str'>,
  'return': <class 'int'>
  }
```

Isso nos retorna um dicionário onde a chave é o nome do parâmetro e o valor é o tipo com o qual esse parâmetro foi anotado.

A key `return` é reservada e representa o tipo retornado pela função, mas não precisaremos dela para essa nossa análise.

Os typehints podem também ser strings, assim:

```python
  async def func(a: "int", b: "str"):
    ...
```

Essa construção é útil quando o tipo que você precisa ainda não foi declarado ou não está disponível em tempo de escrita do código.

Se olharmos o atributo `__annotations__` dessa nova função vemos que os tipos no dicionário retornado são na verdade strings, veja:

```python
    async def func(a: "int", b: "str"):
      pass

    print(func.__annotations__)
    {'a': 'int', 'b': 'str'}
```

Isso é muito ruim pois temos que "parsear" essa string de alguma forma e transformar isso em um tipo python de verdade.

Mas alguém já pensou nisso e criou uma forma de fazer esse parsing automaticamente pra nós. Basta usar a função `typing.get_type_hints()`, assim:

```python
    import typing
    async def func(a: "int", b: "str"):
      pass

    print(typing.get_type_hints(func))
    {'a': <class 'int'>, 'b': <class 'str'>}
```

Veja como agora o dicionário já veio com os tipos python reais.

Se algumas das strings não puderem ser resolvidas para "tipos concretos" uma exception será lançada.

{{<highlight python>}}
    import typing
    async def func(a: "bla"):
      pass


    print(typing.get_type_hints(func))
    NameError: name 'bla' is not defined
{{</highlight>}}

Dessa forma podemos ter certeza que todos os tipos existem e que podemos usá-los no momento de analisar uma assinatura para fazer a chamada.

## Estratégia para passar dinamicamente parâmetros para uma função

Agora já temos quase tudo que precisamos para conseguir analisar dinamicamente uma função e poder escolher quais parâmetros serão passados pra ela.

O que está faltando é justamente o valores que podem ser passados.

Normalmente quando estamos escrevendo um código nós já temos esses valores nas mãos e fazemos a chamada diretamente:

```python
    async def func(a: int, b: str):
      pass

    num = 42
    name = "Dalton"
    await func(num, name)
```

Pensando na nossa análise dinâmica temos que lembrar que nesse caso esses valores viriam de algum lugar e seriam acumulados ao longo da execução do código e poderiam ser usados para ajudar e escolher o que será passado no momento de chamar uma função.

Uma forma válida de acumular esses valores seria em uma espécie de "repositório de tipos", que poderia ser também um dicionário onde a `key` é o tipo e o `value` é um valor daquele tipo. Esse repositório seria usado como fonte de consulta no momento de escolher o que será passado na chamada.

Algo nessa linha:

```python
    async def func(a: int, b: str):
      ...

    await call_func(func, types_repository)
```

Aqui nesse caso a implementação do `call_func` é que teria a lógica de olhar os `__annotations__` e procurar no `types_repository` se existem valores para cada um dos tipos que a função `func` quer receber.

De tudo que vimos até agora o mais importante é: Temos um conjunto de valores que são acumulados em algum lugar (com seus respectivos tipos) e que podem ser usados como fonte de consulta no momento de chamar uma função qualquer.

## Prova de conceito de um Repositório de tipos

Aqui vamos implementar uma versão bem simplificada do que poderia ser um Repositório de tipos. Essa implementação pode ser tão simples quanto um `dict` python comum.

Algo nessa linha:

```python
    from typing import Dict, Type, Any

    types_registry: Dict[Type, Any] = dict()
```

## Prova de conceito de uma implementação da função call_func()

Aqui vamos usar o repositório de tipos (aqui um simples `dict`) para confirmar que é possível fazer uma chamada a uma função (ou método) analisando dinamicamente sua assinatura.

O código abaixo é um exemplo **bem simples** de uma implementação

{{<gist daltonmatos cd423d265ba092300f65ac00af37c8c4 "dynamic-sig-call.py">}}

Quando rodamos esse código vemos que nas duas linhas do `print()` a funcão `func(a: int, b: str)` é chamada corretamente.

```text
    $ pipenv run python dyn-call.py
    int is 42, str is Dalton
    int is 42, str is Dalton
```

Vejam que esse exemplo é **muito** simplificado. Não tratamos aqui, por exemplo, caso de parametros opcionais, parametros que são uma lista, múltiplos parametros de um mesmo tipo. Aqui fizemos apenas uma Prova de Conceito para mostrar que é possível fazer a analise da assinatura e a chamada à função.

# Conclusão

É claro que não vamos mudar nosso código do dia a dia para passar a chamar os métodos de forma dinâmica descobrindo quais valores devem ser passados, mas ter a possibilidade de fazer isso pode ser muito útil em alguns contextos.

Um deles pode ser a implementação de um handler http que não recebe o objeto `Request` e pode já receber o conteúdo do corpo desse `Request` já validado e em forma de uma objeto python.

Um exemplo simples:

```python
    async def save_user(request: Request):
      ...
```

Mudaria para algo como:

```python
    async def save_user(user: User):
      ...
```

Nesse caso algum código anterior à execução desse handler, um middleware por exemplo, já extraiu o corpo do request e já criou o objeto `User` que será passado ao handler.

O framework http poderia usar o que vimos nesse post para analisar a assinatura do handler em questão e fazer a chamada passando os parâmetros necessários de forma dinâmica.

Escrevi sobre isso em outro post onde mostro um exemplo de uso dessa técnica em um handler do asyncworker.  [Asyncworker: Handler Http Recebendo Mais Do Que Request]({{<relref "asyncworker-handler-http-recebendo-mais-do-que-request.md">}})
