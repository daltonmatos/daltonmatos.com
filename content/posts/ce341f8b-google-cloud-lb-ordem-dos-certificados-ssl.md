
---
title: Quando o ordem alfabéticas de certificados SSL faz diferença
author: Dalton Barreto
date:
tags: [infra, gcp, cloud, ssl]
---

Ideia geral:
 Se você tem um LB com um certificado para `teste.daltonmatos.com` e esse certificado se chama `teste-ssl-cert`.
 Se você anexa um segundo certificado nesse mesmo LB, para o mesmo DNS mas que **o nome** seja, por exemplo, `a-teste-ssl-cert`, ou seja, que na ordenação alfabética venha **antes** do outro certificado o LB vai começar a retornar erros de SSL.

 Isso provavelmente acontece pois o primeiro certificado para o nome que o LB encontra é o que ele usa, e como esse novo certificado ainda está em processamento o request falha. O LB **não usa** o segundo certificado, mesmo ele já sendo válido e para o mesmo DNS do request.

 Como validar:

 - Cria um LB com cert válido para `teste.daltonmatos.com`
 - Gera um segundo cert, com nome alfabéticamente anterior, para o mesmo DNS, mas não anexa ao LB.
 - Muda o IP do público do LB. (ou muda apenas o apontameno do DNS, mais fácil)
    - Validar se o certificado que era válido, continua válido.
 - Nesse ponto temos:
    - Cert valido e anexado do LB para `teste.daltonmatos.com`
    - o DNS `teste.daltonmatos.com` atualmente aponta para o IP antigo do LB (ou para um IP errado mesmo...)
    - Um cert não gerado, para o mesmo DNS.
 - Aqui podemos fazer:
    - `curl --resolve ...` quando o LB tem apenas o cert válido.
    - `curl --resolve ...` quando LB tem os dois certs. Aqui as requests devem começar a falhar.


# Imagens

- LB com certificado correto
- LB com os dois certificados, o certo e o errado. Mostrando a ordem em que eles ficam.
- Request funcionando
- Request falhando.
- Se pudermos fazer um vídeo (GIF?) mostrando:
    - LB OK
    - Request OK
    - Edita LB e adiciona cert errado
    - Requests começando falhar


# Resumo da história

Se você precisar migrar um cert (por alguma razão) de um LB e precisa anexar outros certs nele mas que respondem pelo mesmo DNS de um cert que ele já tem, lembre-se de gerar os novos certs com nomes alfabeticamente "depois" dos atuais.

O interessante disso é que esse nome que você gerou, para o novo cert, será definitivo. Ou seja, não dá pra gerar um `temp-*` e remover depois, pois quando você for fazer a "segunda" migração pra remover o `temp-*` e gerar um cert que é ordenado antes dele, você volta ao problema inicial.

Sim, esse caso é MUITO peculiar mas pode acontecer. No meu caso eu estava migrando certificados que antes eram gerenciados pelo kubernetes (cluster GKE) e passariam a ser gerenciados diretamente pelo GCP (sem a necessidade de ter um ManagedCertificate no GKE). Por isso precisei ter dois certs para o mesmo nom em um LB.
