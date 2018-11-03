---
title: Múltiplos certificados SSL com Let's Encrypt e traefik
author: Dalton Barreto
date: 2018-10-08
tags: [traefik, ssl, letsencrypt, certbot]
---

O que o let's encrypt trouxe foi a possibilidade de gerar certificados de forma simples, gratuita e automatizada.

Gerar um certificado é tão simples quanto rodar **um comando**. O única coisa que você precisa ter em me te é como comprovar que você controla o domínio para o qual você está gerando um certificado.

# Challenge http-01

Um dos challenges mais comuns é usar um server http para comprovar que você controla o domínio. Esse tipo de challenge é útil quando você está gerando um certificado para uma máquina que é pública, ou seja, os servidores do let's encrypt vão conseguir acessá-la para comprovar que você tem o controle do domínio.

Mas e quando você precisa gerar certificados que serão usados em máquinas privadas?

# Challenge dns-01

Esse tipo de challenge é super útil para podermos gerar certificados a partir de máquinas privadas. Isso porque a confirmação do controle do domínio é feita via registro DNS.

Para esse challenge funcionar o DNS deve ser possível de resolver publicamente. Se você está gerando um certificado para uma zona **privada** esse challenge não servirá.

# Traefik

[Traefik](https://traefik.io/) é um Proxy reverso capaz de descobrir automaticamente a localização dos backends para os quais ele fará forward das requisições. Isso é especialmente útil em ambientes dinâmicos onde as aplicações podem eventualmente mudar de lugar dentro de um mesmo cluster.

# Certbot

O [Certbot](https://certbot.eff.org/) é o cliente oficial para gerar certificados usando a infraestrutura do [let's encrypt](https://letsencrypt.org/).

Apesar do certbot gerar os certificados sempre em arquivos diferentes ele mantém um symlink apontando sempre para o certificado mais atual.

Isso é **muito** útil pois para você que vai usar esse certificado, basta apontar na configuração do seu servidor esse caminho fixo. Sempre que você gerar um novo certificado, basta pedir ao servidor para recarregar os certificados atuais e pronto, você tem novos certificados disponíveis e sem precisar reiniciar o servidor web.

# Hot reload com Traefik

O problema começa porque o traefik, segundo a documentação, não possui um signal próprio para recarregar as configurações.

Geralmente você envia um `HUP` (kill -HUP `<pid>`) para o processo e ele recarrega todas as suas configurações. Mas o traefik não tem isso implementado então essa não é uma opção válida.

Resta então a opção de pedir ao traefik para vigiar um determinado arquivo de configuração e sempre que esse arquivo sofrer quaisquer mudanças, o traefik vai reler esse arquivo e reaplicar essas configurações.

Aqui problema do certbot manter sempre um caminho fixo (que é um symlink que aponta para o certificado correto) começa a atrapalhar, isso pois como o caminho não muda o Traefik acha que você ainda está usando os mesmos certificados e não recarrega nada.

# certbot deploy-hook

E é aqui que entra o principal desse post: Um deploy-hook que escrevi para resolver esse problema.

O que esse deploy hook faz é gerar um trecho de configuração que aponta para os certificados corretos, mas em vez de usar o symlink gerado pelo certbot ele segue esse symlink e usa o path final do arquivo do certificado, dessa forma a cada novo certificado gerado um novo arquivo de configuração será criado. Isso faz o traefik perceber a mudança e recarregar o certificado.

Vejamos no detalhe como funciona:

# Configuração do Traefik

O traefik precisa ser configurado de forma especial, principalmente no que diz respeito às configurações de certificados SSL.

Esse é o trecho onde os entrypoints são criados, que são quem abrem as portas.

```
defaultEntryPoints = ["http"]
[entryPoints]
  [entryPoints.http]
  address = "{{TRAEFIK_BIND_IP}}:80"

  [entryPoints.https]
  address = "{{TRAEFIK_BIND_IP}}:443"
  [entryPoints.https.tls]
```

Aqui a variável `TRAEFIK_BIND_IP` representa apenas o IP no servidor onde o os respectivos entrypoints abrirão suas portas. Pode ser vazio inclusive (ficando `:80` e `:443`) nesse caso o bind será feitos em todas as interfaces disponíveis.

Perceba que no entrypoints que chamamos de `https` estamos mencionando a configuração sobre `tls`, com essa linha:

```
[entryPoints.https.tls]
```

Agora instruímos o traefik a vigiar uma pasta onde ele ficará procurando por arquivos de configuração adicionais.
É lá que vamos colocar nossas configs que apontam para nossos certificados:

```
[file]
directory = conf.d/
watch = true
```

O que isso faz é: Quaisquer arquivos de configuração nessa pasta serão carregados pelo traefik e não só isso, caso haja qualquer mudança nesses arquivos o traefik vai recarregá-los. Isso é o que queremos.

## Configuração de um certificado SSL

Esse é um trecho de exemplo em que adicionamos um novo certificado ao traefik.

```
[[tls]]
  entryPoints = ["https"]
  [tls.certificate]
      certFile = "/etc/letsencrypt/live/<domain>/fullchain.pem"
      keyFile = "/etc/letsencrypt/live/<domain>/privkey.pem"
```

Basta colocar um arquivo com esse conteúdo na pasta `conf.d/` que automaticamente o entrypoint `https` (que está na porta `443`) vai passar a conhecer esse certificado e a partir daí você já será capaz de fazer requisições HTTPS para esse traefik.

Vejamos um exemplo:

Se usarmos o certbot pra gerar um certificado para `app.daltonmatos.com`, teríamos que adicionar esse trecho de config na pasta `conf.d/`:

```
[[tls]]
  entryPoints = ["https"]
  [tls.certificate]
      certFile = "/etc/letsencrypt/live/app.daltonmatos.com/fullchain.pem"
      keyFile = "/etc/letsencrypt/live/app.daltonmatos.com/privkey.pem"
```

Esse path, na verdade, aponta para `/etc/letsencrypt/archive/app.daltonmatos.com/privkey1.pem`. À medida que vamos renovando esse certificado o certbot vai gerando novos arquivo na pasta `/etc/letsencrypt/archive/app.daltonmatos.com/` com nomes `privkey2.pem`, `privkey3.pem` e assim por diante.

E aqui entera o deploy-hook que escrevi para podermos gerar os techos de configuração sempre usando os paths da pasta `archive/` e não da pasta `live/`.

# Implementação do certbot deploy-hook

O [deploy-hook](https://certbot.eff.org/docs/using.html#renewing-certificates) é uma forma de pedir ao certbot que chame um comando escolhido por você sempre que um certificado for renovado **com sucesso**.

O que nosso deploy-hook faz é descobrir o path final do certificado. Esse é o código:

{{<highlight python>}}
import os
from jinja2 import Environment, BaseLoader
from hooks import conf


SSL_CONFIG_TEMPLATE = """
[[tls]]
  entryPoints = ["https"]
  [tls.certificate]
      certFile = "{{certfile_path}}"
      keyFile = "{{keyfile_path}}"

"""

def generate_config_file_for_certificate(output_path, lineage_path):
    content = render_config_for_certificate(lineage_path)
    outputfile = os.path.join(output_path, os.path.basename(lineage_path.strip("/")))
    outputfile += ".toml"
    with open(outputfile, "wa") as outfile:
        outfile.write(content)

    return outputfile

def render_config_for_certificate(live_folder):
    certfile_path = os.path.join(live_folder, "fullchain.pem")
    keyfile_path = os.path.join(live_folder, "privkey.pem")
    return render_template(resolve_symlink(certfile_path), resolve_symlink(keyfile_path))

def render_template(certfile_path, keyfile_path):
    jinja2_env = Environment(loader=BaseLoader())
    rendered_config = jinja2_env.from_string(SSL_CONFIG_TEMPLATE).render(
        certfile_path=certfile_path, keyfile_path=keyfile_path
    )
    return rendered_config

def resolve_symlink(symlink):
    link = os.readlink(symlink)
    return os.path.abspath(os.path.join(os.path.dirname(symlink), link))

def main():
    rendered_config = generate_config_file_for_certificate(conf.CERTBOT_HOOK_OUTPUT_DIR, conf.CERTBOT_RENEWED_LINEAGE)
    p
{{</highlight>}}


Qual a ideia? O que esse código faz é o seguinte:

Assim que um novo certificado é gerado, esse código será chamado e vai:

* Olhar o arquivo `/etc/letsencrypt/live/<certname>/<filename>.pem`;
* Descobrir para onde esse symlink aponta;
* Gerar um trecho de config para o Treafik contendo o destino final do certificado.

Além disso, vai gravar esse conteúdo na pasta apontada pela ENV `CERTBOT_HOOK_OUTPUT_DIR`. O nome do arquivo é o mesmo nome do certificado que acabou de ser renovado.

Então se apontamos essa ENV para a mesma pasta onde o Traefik está esperando por novos arquivos de config podemos ter a renovação automatica dos certificados **com** reload feito pelo Traefik de forma automatica e transparente, sem precisar reiniciar nada.



