---
title: "(Arch) Linux Com Full Disk Encryption"
date: 2018-08-01T21:41:17-03:00
draft: true
tags: [linux, crypt, luks]
---

Atualmente é tão simples e transparente ter o disco encriptdo que não faz sentido não ter. Se você pensar na
possível perda de performance (pelo fato do seu disco estar sendo encriptado/decriptado em tempo de execução)
vai perceber que, a não ser que você faça um uso **muito específico** do seu PC, essa "perda de performance"
não fará nenhuma diferença.

Sempre que me perguntam se a performance de um disco encriptado é boa ou rum, eu respondo que não sei pois nunca
tive um laptop onde o disco não estava encriptado.

# Quando é simples instalar com Linux com disco encriptado?

Qualquer distro onde você precise fazer um `chroot` como parte da instalação é trivial ter o disco completamente
encriptado. Isso porque para o processo de instalação, pouco importa se o disco montado está encriptado ou não, basta que
ele esteja montado no lugar certo, geralmente `/mnt/`.
