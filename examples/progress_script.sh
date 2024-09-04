#!/bin/bash

for i in {1..100}
do
    echo "スクリプトファイルで実行中..."
    echo "Progress: $i%"
    sleep 0.5
done
echo -ne "\n"  # プログレスバーが完了した後に改行

for i in {1..100}
do
    echo $i
    sleep 0.1
done
