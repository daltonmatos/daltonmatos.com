#!/bin/bash

# Gera o CSS final para o site


cd bootstrap.css/
patch -p1 < ../css-src/patterns.patch
cd ..
echo "Gerando CSS final"
lessc css-src/daltonmatos.less > daltonmatosdotcom/static/css/site.css

cd bootstrap.css
git reset --hard
