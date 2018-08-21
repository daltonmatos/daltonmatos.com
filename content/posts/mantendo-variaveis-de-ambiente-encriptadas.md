---
title: "Mantendo variáveis de ambiente encriptadas"
slug: mantendo-variaveis-de-ambiente-encriptadas
date: 2018-08-16
author: "Dalton Barreto"
tags: [crypt, gpg, gnupg, shell]
---

Desde que me interessei mais sobre encriptação, chaves GPG e afins comecei a tentar montar um workflow que fosse ao mesmo tempo agradável e seguro (para os padrões que escolhi).
Depois de ter começado a usar um [smartcard](/tags/yubikey) para armazenar minhas chaves ([[1]](/2018/07/preparando-uma-yubikey-4-nano-para-uso-diario/) e [[2]](/2018/08/usando-seu-keyring-gpg-para-guardar-sua-chave-ssh/)) comecei a usá-lo em vários pontos do meu dia a dia que achei que deveriam/poderiam ser mais seguros.

# Variáveis de ambiente

Variáveis de ambiente, ou apenas `ENVs` são muito comuns no dia a dia de quem lida com desenvolvimento. Seja para passar parametros para o seu código ou para configurar seu shell, elas estão lá muitas vezes até mesmo sem a gente se dar conta.

Por muito tempo guardei credenciais de acesso em `ENVs`, por pura praticidade. Afinal, não precisaria decorar nenhum daqueles valores e poderia, com um comando, resgatá-los e usar quando necessário.  Mas o problema é que esses valores ficam guardados em texto plano. Isso é análogo a anotarmos a senha do nosso cartão do banco em uma arquivo `txt` dentro do nosso computador, e não fazemos isso né?

Por isso faz um tempo que pensei em qual seria o custo de manter todas as minhas `ENVs` encriptadas e mais, queria continuar dependendo apenas de um comando para recuperar seus valores e usá-los.


# Encriptando suas Variáveis de ambiente

A encriptação não sem nenhum mistério, é passar um valor para o `gnupg` e guardar o resultado na `ENV` desejada. Como o resultado da encriptação é um valor multi-linha, precisamos manter esse "formato". Aqui está um exemplo de como gerar uma variável dessas.

Aqui vamos apenas chamar o comando mostrado, colar o conteúdo a ser encriptado e dar um `Enter`.

Depois pressione `^D` (`Ctrl+d`). Precisamos disso porque o `gnupg` está lendo do `stdin` e o `^D` é o sinal de que a entrada terminou.

{{< highlight zsh>}}
$ gpg -e -r daltonmatos@gmail.com
AQUI VAI O CONTEÚDO SENSÍVEL
-----BEGIN PGP MESSAGE-----

hQIMA0V2jZ1vFNR0AQ/+IH3DEZZJ8dLefN1BHxUtiod5nniKD/JUrD9WUIv8fny4
pIfMHdOppfyFH57P4+nAFN10dn09iRqPEiGMl2C2OiyLKapW9FmR5P9JutRDK4bE
BkOoJyxVtIOJQNsixbUcvxQJzWovnOEXklV/F++OntzpwvKln5BHdmAIFKJ1kUbd
jiaJsySezqktQxV1o0qwILQjTJNlsig4sOGljyfzlicI09fp/+zHXvunw+Wo3zND
LKwun1xbpg8ppepl1WSBTP00cf2OdMdyAts3JYNA7A0x+I1NLqJ3lfn9gtJ6YErU
zqcT8Ac8jivaCzWq4CArb7YrSV904okHz/OreJg0nbcKXlbR4SYND0aFGQMek+Yl
WbNODvKL2Q3FABECsOAtmPtYLn3kLrqcuz5RKacCs0jfxS5N6p7b6VI6ZpX39Z+3
1Ox3JBkXKmZDs26MSUvX4tFZGSl8K9Sf+rB3dlF+F8wBHbhhTWl6AlLSGFrtZXlW
4jFXn/3BAEmF8UzfV0VDtuVApXbqgQLzelb/oaO/tdr2zzUqluq0c5L63LacKSzt
3y33+bJL4ezLPWXCUtLvu4n0Krl2UYVJZJuy9rVaGguP/MYKjFp5pfCy8XjYUE0v
U4QzWxVe9RNAmhe0fW0ivjuMNtzlS7BqAwTqMugzBeWw8/uXoT4tCtCqAJF4eMTS
QgFVR9Ybw5m1IANObGBPKBdwAMkd4wsYNvjPGNgu5S01YGbt+qjt/P9JhZzAvSxO
pPWRurxuZxJmRsUJy1gzQrUbcA==
=lCiu
-----END PGP MESSAGE-----
{{< /highlight >}}

Agora salvamos isso em algum arquivo que será importado pelo nosso shell. Eu tenho essas (e outras) coisas em um arquivo `~/.shell-extras`, mas pode ser em qualquer lugar, desde que seja importado pelo seu shell.

{{<highlight zsh>}}
export CRYPT_API_AUTH_TOKEN="
-----BEGIN PGP MESSAGE-----

hQIMA0V2jZ1vFNR0AQ/9FqSgxyz5hdrwTiYNEkvPf4s+IvXophjbR9dxfRj2shYq
KNRNa9uXy3dvOO8A622svXwHqaOrkbwCdzDqNCP2pBArXASCHVsLagjA+s5TNAQc
2bcyEVdmxxMK3ldXA5dJtoc68NH0sJztmtA9cLt9OhCOZ6SA/gw8cn7+4uLjsT20
olHrLAKboxiO5HuCQ9TiqLOLBgvjCGqUt3aI25wP+hTkL/qgrE4V+TcgRc7kFjZc
B0DATPo8Gt3P+D358Y/BoKLVkaxM03CEdIjv81JEc/5EQhCzFabzN0WsP00H9mHD
sq0PWGDAbTR/R4jBJDPJ7l0Yoj/lvzMPRtc+JcS26vHYmABJlGUSJeSZccwVe2k2
FZgK1XJDCYMThr2XKjU2TEOWJhQVUbPusshFh7FOY8NEBEH8pbyrhVptt3wMsjVl
ooyYS9bmrTxn+XAE60WlGSsTpGBmYJ+uolicMq7Pc0kY5RfIBPf2z0ZcD/mM95T6
fbtDEh1d0zCSW1e6LnZmkLMDCo5oON5LheuVRMOEFgmXJ+CdYtfk9oGB2m+PBZeL
okERrJPGDcoto57WZTURRvQVIgDeDPzMA/R04+6IgOgenMYTPuw2wEYLqBWrp4+t
ndgfLejrMWiI2CKE6xRMbmTyNcGwi1g+9g0qhQeJy4ZwNX+kcve1hPHpzaFww+zS
QgEd+8nKUazScIobLjhtJwOAqwKe0dJN23Mw50OFFAmSndjBcWeJD+Hb820wUZV7
mMFvsc7xLBzsdsioIQCQdnEwHQ==
=JCIv
-----END PGP MESSAGE-----
"
{{</highlight>}}

Para fazer um teste rápido podemos rodar:

{{<highlight zsh>}}
printenv CRYPT_API_AUTH_TOKEN | gpg -d
gpg: encrypted with 4096-bit RSA key, ID 45768D9D6F14D474, created 2017-09-14
      "Dalton Barreto <daltonmatos@gmail.com>"
AQUI VAI O CONTEÚDO SENSÍVEL
{{</highlight>}}

Isso vai nos dar o resultado original. Essa é a confirmação de que tudo está correto e já podemos usar esse valor em quaisquer comandos em nosso shell prompt (ou script!).


# Usando uma variável em um comando qualquer

O uso na linha de comando é bem simples, na verdade o que temos que fazer é encaixar esse `printnev` que fizemos aí em cima no meio da linha de comando onde precisamos usar o valor sensível. Algo assim:

{{<highlight zsh>}}
curl -H "X-Secret: $(printenv CRYPT_API_AUTH_TOKEN| gpg -d)" https://httpbin.org/headers            
gpg: encrypted with 4096-bit RSA key, ID 45768D9D6F14D474, created 2017-09-14
      "Dalton Barreto <daltonmatos@gmail.com>"
{
  "headers": {
    "Accept": "*/*", 
    "Connection": "close", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.61.0", 
    "X-Secret": "AQUI VAI O CONTEÚDO SENSÍVEL"
  }
}
{{</highlight>}}

Veja como o header `X-Secret` foi enviado contendo o valor da nossa `ENV`, já decriptado.

## Facilitando o uso desses valores em nossos comandos

Para não precisar digitar todo esse comando do `printenv` sempre que precisar usar alguma `ENV`, escrevi uma shell function que facilita esse uso. Chamei essa function de `decrypt_env`. O que ela recebe como parametro é apenas o nome da env e retorna seu valor, decriptado.

Para poder diferenciar, pelo nome, envs que são encriptadas sempre uso o prefixo `CRYPT_` em todas as `ENVs` que possuem conteúdo encriptado. Essa shell function é bem simples:

{{< highlight zsh >}}
decrypt_env() {
  local env_name_sufix=$1
  local env_name=CRYPT_${env_name_sufix}
  gpg -d <<<${(P)env_name} 2>/dev/null
}
{{</highlight>}}

Esse código está no meu [dotfiles](https://github.com/daltonmatos/dotfiles/blob/master/zsh/zshrc#L194-L198).

De posse dessa função, nossa linha de comando de exemplo ficaria assim:

{{< highlight zsh >}}
curl -H "X-Secret: $(decrypt_env API_AUTH_TOKEN)" https://httpbin.org/headers           
{
  "headers": {
    "Accept": "*/*", 
    "Connection": "close", 
    "Host": "httpbin.org", 
    "User-Agent": "curl/7.61.0", 
    "X-Secret": "AQUI VAI O CONTEÚDO SENSÍVEL"
  }
}
{{</highlight>}}

Perceba que passamos apenas o "nome" da env, sem mencionar o prefixo `CRYPT_`. Outra coisa que a function faz é suprimir o que o `gnupg` imprime no `stderr`, apenas para não termos eventuais problemas, já que estáriamos alterando o `stderr` do shell e essa function deveria ser totalmente transparente.

**Nota**: Confesso que tentei, em algum momento, escrever um auto-complete para o zsh, mas falhei. Talvez eu volte nisso algum dia. =)

# Histórico do shell

Uma vantagem colateral dessa abordagem é que os valores sensíveis que estão nessas `ENVs` **não ficam** no histórico do seu shell, afinal lá só estará o comando com a chamada à função `decrypt_env()`. Nesse caso não temos nenhum vazamento de informações sobre seus valores sensíveis.

Atualmente todas as minhas `ENVs` sensíveis estão encriptadas e isso me faz sentir mais seguro em relação ao que pode ser lido em um eventual acesso à minha estação de trabalho ou computador pessoal.

