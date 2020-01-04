---
title: Escrevendo workers assíncronos em python com asyncowrker
author: Dalton Barreto
date: 2019-03-21
tags: [python, async, asyncworker]
---

Olhando o histórico de commits, o primeiro data de 19/Jan/2017. Essa talvez seja a data oficial do início do que chamamos de [`asyncworker`](https://github.com/B2W-BIT/async-worker).

O projeto nasceu para facilitar a escrita de workers assíncronos em python. Inicialmente eram workers para rabbitmq. Mas com o tempo surgiram oportunidades de implementar suporte a outros "backends", por assim dizer.

# Backends atualmente suportados

Até a data de hoje o projeto suporta os seguintes backends:

- RabbitMQ
- Server Side Events
- HTTP
- Tarefas recorrentes

E a ideia é adicionar suporte a mais backends com o tempo.

Nesse post vamos ver um pouco da ideia geral do framework e no detalhe como escrever um worker para RabbitMQ.

# Estrutura do código de um worker

A forma de se escrever um worker com o [asyncworker](https://github.com/B2W-BIT/async-worker) foi muito inspirada no [flask](http://flask.pocoo.org). É uma sintaxe simples e limpa onde você escreve uma função e adiciona a essa função um [decorator](https://docs.python.org/3/glossary.html#term-decorator) que vai efetivamente registrar esse função para ser usada quando o código estiver rodando.

Pense no [asyncworker](https://github.com/B2W-BIT/async-worker) como um framework genérico para implementação de handlers, onde esses handlers podem receber informações de várias origens distintas, é aqui que entram os "backends" que citei acima.

Então a ideia geral da estrutura de um handler é a seguinte:

{{<highlight python>}}
from asyncworker import App, RouteTypes
app = App(...)

@app.route([..., ...], type=RouteTypes.<TYPE>, options={})
async def myhandler(...):
    ...
    ...
{{</highlight>}}

O que estamos vendo aqui?

Primeiro construímos nossa `App`. Esse é o ponto central do seu código. Ali estará registrado tudo que é necessário para que seus handlers possam trabalhar e fazer, cada um, o seu papel.

Depois vem a definição propriamente dita do handler. Ele é decorado com `@app.route()`e é aqui que a mágica acontece.

É nesse momento que escolhemos de qual tipo esse handler vai ser, ou seja, de onde virão os estímulos que farão esse handler ser executado.

Isso é o mínimo necessário para se escrever um handler que fará alguma coisa.

Nesse post veremos como usar o backend RabbitMQ para escrever um handler assíncrono.

# Usando sua App como storage de configurações

A `App()` que você cria se comporta também como um dicionário. Isso significa que você pode guardar o que quiser ali dentro.

Por exemplo, parainiciar um logger assíncrono podemos fazer:

{{<highlight python>}}
    import logging
    from asyncworker import App
    from aiologger.loggers.json import JsonLogger

    new_app = App(...)
    async def init_app(app: App):
      app["logger"] = JsonLogger.default_with_handlers(level=logging.INFO)

{{</highlight>}}

**Nota**: Se quiser saber mais sobre log assíncrono em python, veja [esse post aqui](https://medium.com/@diogommartins/aiologger-logger-assíncrono-para-python-e-asyncio-ba0b20a7b31e) e também [o código do projeto](https://github.com/b2w-bit/aiologger).

A partir do momento em que chamarmos a função `init_app()` sempre que acessarmos `app["logger"]` teremos um logger assíncrono já configurado para gerar logs no formato JSON usando stdout/stderr.

A ideia é que funções como essa sejam chamadas apenas durante a inicialização da nossa app, que é o que veremos logo a seguir.

# Registrando callbacks de startup e shutdown

Para isso o [asyncworker](https://github.com/B2W-BIT/async-worker) permite que você registre callbacks de startup e shutdown para a sua app.

Como estamos lidando com código assíncrono e é (ainda) impossível chamar código assíncrono no momento em que um módulo python é importado, as inicializações que antes fazíamos no import do módulo agora devem ser feitas dentro de funções específicas.

Esses callbacks também são registrados com decoratos.

{{<highlight python>}}
from asyncworker import App, RouteTypes
from asyncworker.options import Options

app = App(...)

@app.run_on_startup
async def start_up(app):
    print("Starting App...")

@app.run_on_shutdown
async def shut_down(app):
    print("Shutdown app")
{{</highlight>}}

# Escrevendo um worker para RabbitMQ

Aqui vamos ver um exemplo funcional de um worker que pode ser rodado na linha de comando:

{{<highlight python>}}
from asyncworker import App, RouteTypes
from asyncworker.options import Options
from asyncworker.rabbitmq.message import RabbitMQMessage

app = App("localhost", "guest", "guest", 1024)

@app.route(
    ["items"], type=RouteTypes.AMQP_RABBITMQ, options={Options.BULK_SIZE: 2014}
)
async def check(msgs):
    for m in msgs:
        print(m.body)

app.run()
{{</highlight>}}

Vamos analisar os parâmetros que estamos passando aqui.

Na linha de construção da `App()` passamos as credenciais de acesso ao RabbitMQ. Passamos também o parâmetro de `prefetch`, que diz quantas mensagens o RabbitMQ poderá entregar a esse consumer mesmo sem ele pedir.

Agora vamos analisar a linha do `@app.route()`. O primeiro parâmetro é uma lista de nomes de filas que fornecerão mensagens para esse handler. Perceba que, como esse parâmetro é uma lista, podemos usar um mesmo handler para consumir de múltiplas filas diferentes.

O `type=RouteTypes.AMQP_RABBITMQ` é auto explicativo. Estamos selecionando qual o tipo de backend fornecerá dados a esse handler.

Agora a parte do `options=`. Essa opção serve para passarmos quaisquer tipos de opções adicionais para cada tipo de backend. Aqui estamos usando a opção `BULK_SIZE`. Essa opção permite que o asyncworker entregue as mensagens para o handler em "lotes" com tamanho de no máximo `BULK_SIZE` itens. Aqui temos uma observação importante: O valor final escolhido para o tamanho do lote é `min(prefetch, BULK_SIZE)`.

Pensa em um handler que precisa processar muitas mensagens e gravar dados dessas mensagens em um storage. Em casos onde esse storage aceita operações em lote (como ElasticSearch e MongoDB, por exemplo) o handler pode se aproveitar disso e mandar os dados para o storage também em lote.

Se você não específica o tamanho do lote, o valor padrão é 1. Isso significa que seu handler sempre recebe uma lista, mesmo quando está recebendo apenas uma mensagem de cada vez.

Por padrão, caso o seu handler não levante nenhuma exceção, todas as mensagens do lote são confirmadas no RabbitMQ. Esse comportamento pode ser mudado com mais opções no parâmetro `options=`. Por exemplo, esse código abaixo joga fora quaisquer mensagens que gerem erros no momento em que o handler roda.

{{<highlight python>}}
from asyncworker import App, RouteTypes
from asyncworker.options import Options, Events, Actions

app = App("localhost", "guest", "guest", 2014)


@app.route(
    ["items"],
    type=RouteTypes.AMQP_RABBITMQ,
    options={Options.BULK_SIZE: 2014, Events.ON_EXCEPTION: Actions.REJECT},
)
async def check(msgs):
    for m in msgs:
        print(m.body)
        1 / 0
{{</highlight>}}

Nesse caso, estamos provocando um exceção do código do handler e a opção `Events.ON_EXCEPTION: Actions.REJECT` fará com que as mensagens sejam rejeitadas, ou seja, jogadas fora automaticamente. Os eventos diponíveis para os handlers são: `Events.ON_EXCEPTION` e `Events.ON_SUCCESS` e as Actions são `Actions.ACK`, `Actions.REJECT` e `Actions.REQUEUE`. Os valores default para essas opções são: `Events.ON_SUCCESS = Actions.ACK` e `Events.ON_EXCEPTION = Actions.REQUEUE`.

# Escolhendo a ação que será tomada em cada mensagem, individualmente

Além dessa ação padrão você pode escolher, individualmente, se cada mensagem vai ser confirmada ou devolvida pra fila.

Então imagina que do lote de 512 mensagens que um handler recebeu, as 100 primeiras deram problema e precisam ser rejeitadas. Você pode chamar, em cada uma dessas 100 mensagens, o método `.reject()`. Isso vai fazer com que essas mensagens sejam devolvidas para fila, mas o restante seja confirmado, normalmente. Exemplo:


{{<highlight python>}}
    for i in msg:
        try:
           process_message(m)
        except:
           m.reject(requeue=True)
{{</highlight>}}

## Flush automático de mensagens

Nem sempre a quantidade de mensagens que chega ao seu RabbitMQ consegue encher o `BULK_SIZE` que você escolheu, ou seja, mensagens ficariam "paradas" na fila até que o seu "lote" possa encher.

Mas nem sempre podemos esperar por mais mensagens para processar as que estão paradas. Pense em um processo que roda uma vez por dia. Se você escolheu um `BULK_SIZE=1000` e a rodada de hoje gerou 1024 mensagens, essa 24 mensagens adicionais seriam processadas apenas na próxima rodada desse processo, no dia seguinte.

Para resolver isso o asyncworker tem a possibilidade de fazer "flush" das mensagens em un intervalo escolhido por você. Para isso basta mudar o valor da envvar `ASYNCWORKER_FLUSH_TIMEOUT`, que por padrão tem o valor `60`.

Isso significa que, a cada 60 segundos, independente de existirem mensagens suficientes para encher o tamanho do "lote" que você definiu o asyncworker vai enviar quaisquer mensagens adicionais para o seu handler.

Nesse caso do exemplo cima seu handler seria chamado com um lote de 24 mensagens.

## Rodando sua app asyncworker

Para rodar sua app asyncworker, basta chamar `app.run()` na instância de `App()` que você criou. Esse é um exemplo completo de um worker:



{{<highlight python>}}
# worker.py
from asyncworker import App, RouteTypes
from asyncworker.options import Options
from asyncworker.rabbitmq.message import RabbitMQMessage

app = App("localhost", "guest", "guest", 1024)

@app.route(
    ["items"], type=RouteTypes.AMQP_RABBITMQ, options={Options.BULK_SIZE: 2014}
)
async def check(msgs):
    for m in msgs:
        print(m.body)

app.run()

{{</highlight>}}

E esse worker pode ser rodado assim:


{{<highlight zsh>}}
$ python worker.py
{{</highlight >}}

No próximo post veremos como usar um segundo backend do [asyncworker](https://github.com/B2W-BIT/async-worker). Até lá.

Esse blog foi escrito com asyncworker `0.9.0-rc2`.
