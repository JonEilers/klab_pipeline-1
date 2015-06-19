#!/bin/sh

set -e
set -u

for i in $@; do 
  echo $i 
  sed -i.bak -e '2s/)\({[0-9][0-9]*};"\)/):0.0\1/' $i; 
done
