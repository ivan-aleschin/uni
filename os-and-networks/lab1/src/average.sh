#!/bin/bash
# $@ — все аргументы скрипта
count=$#
sum=0
for num in "$@"
do
  sum=$((sum + num))
done
if [ $count -ne 0 ]; then
  avg=$(echo "scale=2; $sum / $count" | bc)
else
  avg=0
fi
echo "Количество аргументов: $count"
echo "Среднее арифметическое: $avg"
