---
title: Múltiplos certificados SSL com Let's Encrypt e traefik
author: Dalton Barreto
date: 2018-10-08
draft: true
tags: [traefik, ssl, letsencrypt, certbot]
---

O que o let's encrypt trouxe foi a possibilidade de gerar certificados de forma simples, gratuita e automatizada.

Gerar um certificado é tão simples quanto rodar **um comando**. O única coisa que você precisa ter em me te é como comprovar que você controla o domínio para o qual você está gerando um certificado.

# Challenge http-01

Um dos challenges mais comuns é usar um server http para comprovar que você controla o domínio. Esse tipo de challenge é útil quando você está gerando um certificado para uma máquina que é pública, ou seja, os servidores do let's encrypt vão conseguir acessá-la para comprovar que você tem o controle do domínio.

Mas e quando você precisa gerar certificados que serão usados em máquinas privadas?

# Challenge dns-01

