---
title: "(Arch) Linux Com Full Disk Encryption"
date: 2018-08-02
tags: [linux, crypt, luks]
---

Atualmente é tão simples e transparente ter o disco encriptdo que não faz sentido não ter. Se você pensar na
possível perda de performance (pelo fato do seu disco estar sendo encriptado/decriptado em tempo de execução)
vai perceber que, a não ser que você faça um uso **muito específico** do seu PC, essa "perda de performance"
não fará nenhuma diferença.

Sempre que me perguntam se a performance de um disco encriptado é boa ou ruim, eu respondo que não sei pois nunca
tive um laptop onde o disco não estava encriptado.

# Quando é simples instalar Linux com disco encriptado?

Qualquer distro onde você precise fazer um `chroot` como parte da instalação é trivial ter o disco completamente
encriptado. Isso porque para o processo de instalação, pouco importa se o disco montado está encriptado ou não, basta que
ele esteja montado no lugar certo, geralmente `/mnt/`.


A instalação da sua distribuição acontece **normalmente**, mudando apenas em 3 pontos, que vou mostrar seguir:

 * Preparação do disco;
 * Configuração do initrd;
 * Configuração do GRUB.

# Particionando o disco

O particionamento é idêntico, só estou escrevendo especificamente sobre ele pois vamos usar um tipo diferente de tabela de partição. Por muito tempo usamos o particionamento `msdos`, há algum tempo surgiu um novo tipo de particionamento, o [GPT](https://en.wikipedia.org/wiki/GUID_Partition_Table) e vamos usá-lo.

O `fdisk` é capaz de gerar partições `GPT` então poderemos usá-lo para essa preparação.

**Atenção**: O que vamos fazer agora destruirá **todos os dados do seu disco**.

```
$ sudo fdisk /dev/sdb
```
Aqui, `/dev/sdb` deve ser o disco onde você está instalando sua distribuição Linux.

Depois pressione `g` e isso fará com que todas as partições sejam removidas e uma nova tabela de partição `GPT` seja criada.

Agora vamos criar as partições. Vamos criar duas partições: Uma para o GRUB e outra para nossos dados. A do GRUB pode ter 64MB (pode até sem **bem** menor se você quiser, afinal aqui ficarão apenas os binários do próprio GRUB) e deve ser do tipo `04 Boot`. A outra pode ser do tipo default (`20 Linux Partition`) e deve ocupar todo o restante do disco.

O particionamento está pronto. Até aqui nada de diferente a não ser o `GPT`, e isso nem tem relação com a escolha de usar encriptação.

Rodando um `fdisk -l /dev/sdb` temos:

```
Device      Start      End  Sectors  Size Type
/dev/sdb1    2048   133119   131072   64M BIOS boot
/dev/sdb2  133120 15974366 15841247  7,6G Linux filesystem
```

# Preparando o disco para a instalação

A preparação do disco acontece quase que igualmente à preparação original, a diferença é que antes de rodar o `mke2fs` você precisa rodar dois comandos para encriptar:

Antes tínhamos essa preparação:
```
$ mke2fs -t ext4 /dev/sdb2
$ mount /dev/sdb2 /mnt
```

Agora temos:

```
$ cryptsetup luksFormat /dev/sdb2
$ cryptsetup luksOpen /dev/sdb2 crypt
$ mke2fs -t ext4 /dev/mapper/crypt
$ mount /dev/mapper/crypt /mnt
```

Nesse ponto você vai ter escolhido a senha de encriptação do seu disco. Essa é a senha que você usará para destravá-lo durante o boot. Esquecer essa senha significa perder tudo que está no seu disco, para sempre. Lembre-se disso.

Pronto. Agora estamos exatamente no mesmo ponto da instalação da sua distribuição quando temos que fazer o chroot.

# Configurando o initrd

Como estamos agora com um disco encriptado, precisamos dizer ao kernel como destravar esse disco para que ele possa fazer o processo normal de boot. Para isso vamos editar o arquivo `/etc/mkinitcpio.conf`. Esse é o arquivo de configuração para o `mkinitcpio`, que é o comando responsável por gerar nosso initrd.

Só precisamos alterar uma linha. Ache a linha `HOOKS="...."` e adicione a essa linha o hook `encrypt`. Certifique-se que esse Hook apareça **antes** do Hook `filesystems`.

Geralmente a linha, depois de ser alterada, fica assim:

```
HOOKS=(base udev autodetect modconf block encrypt filesystems keyboard fsck)
```

# Configurando o GRUB

Para o GRUB precisamos editar duas linhas no `/etc/default/grub`, são elas:

```
GRUB_ENABLE_CRYPTODISK=y
GRUB_CMDLINE_LINUX="cryptdevice=UUID=<UUID>:crypt"
```

Onde `<UUID>` é o valor do UUID da partção que encriptamos, no nosso caso aqui `/dev/sdb2`. Para oncseguir o UUID de uma partição, use o comando `blkid`.

```
$ sudo blkid
/dev/sdb2: UUID="d0eb2665-291f-4010-abf1-da46304a592e" PARTUUID="d939470b-3425-1745-9b8c-503d2be1c2f3"
```

Então nesse caso, nossa linha ficaria assim:

```
GRUB_CMDLINE_LINUX="cryptdevice=UUID=d0eb2665-291f-4010-abf1-da46304a592e:crypt"
```

Instale o GRUB normalmente, termine e instalação da sua distribuição e dê boot.

Bem no início do boot, antes mesmo do menu do GRUB aparecer, o próprio GRUB vai pedir a senha para destravar o disco. 

# Considerações finais

Percebeu que apesar de chamarmos de "Full disk encryption" a partição onde ficam os binários do GRUB ainda está desencriptada? Pois é, e sim esse é um possível vetor de ataque para seu setup. Se alguém com acesso físico à sua máquina conseguir implantar um GRUB "infectado", não tem muito o que você possa fazer, afinal o boot acontecerá normalmente e você não perceberá a diferença.

O GRUB permite que você apresente pra ele um chave pública GPG e ele usará essa chave para conferir a assinatura digital de todos o binários que ele carregar durante o boot ([doc aqui](https://www.gnu.org/software/grub/manual/grub/grub.html#Using-digital-signatures)). Isso diminui bastante o vetor de ataque mas ainda sobra um pedaço. Esse pedaço é o que o próprio GRUB chama de `core.img`. o `core.img` é a parte do GRUB que O SEU HARDWARE carrega. 

Então para proteger seu boot de ponta a ponta, você teria que assinar o `core.img` com uma chave privada que só você tem acesso e apresentar uma chave pública para O
SEU HARDWARE, assim o hardware pode conferir a assinatura e recusar o boot caso alguém tenha alterado um bit sequer dos binários do GRUB (nesse caso o `core.img`).

Para isso existe o [Secure Boot](https://docs.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-secure-boot), mas isso é assunto pra outra hora.

