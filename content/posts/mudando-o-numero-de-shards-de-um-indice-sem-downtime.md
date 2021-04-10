---
title: Mudando o numero de shards de um índice sem downtime
---

falar sobre o reindex com `version_type=external`. Mostrar que podemos fazer multiplos reindex sem problemas. Pois se continuam chegando novos documentos no índice antigo enquanto o reindex está rodando, temos que fazer novamente.

Atenção que os reindex adicionais devem ter algum filtro para pegar apenas "novos" documentos, que foram criados/atualizados após o início do primeiro reindex.

falar sobre a taxa de index no índice novo e no velho. Se a taxa no indice antigo for sempre maior do que a velocidade do reindex, então por um breve momento (a partir da mudança do índice de escrita e durante o último reindex) alguns documentos podem não ser retornados em uma busca. Afinal eles estão apenas no índice antigo e agora o índice "oficial" já é o novo.

Falar sobre alias e que isso poder ser resolvido com ele. Mas quando um alias tem mais de um índice, não podemos fazer get by ID.

Mostrar o código do reindex com filtro e etc.

Lembrar que a ideia é manter: Consistencia dos dados e uptime da aplicação. Mas **não necessariamente** performance.
