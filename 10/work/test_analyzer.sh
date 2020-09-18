#!/bin/sh

TARGET=$1
BASE=$(cd $(pwd)/..; pwd)

ORIG=$BASE/$TARGET
WORK=$BASE/${TARGET}_tmp

cp -r $ORIG $WORK

python3 JackAnalyzer.py $WORK

for filename in $WORK/*T.xml; do
    rm $filename
done

for filename in $WORK/*.xml; do
    name=$(basename $filename)
    echo $name
    TextComparer $ORIG/$name $WORK/$name
done

rm -rf $WORK