#!/bin/bash

# Originally went to 1907 as everything after had a different URL for fr/en
# As of 2020-11=15 the following need to be manually downloaded
# 1912, 1936, 1957, 1958, 1959, 1960, 1961, 1962, 1963
# Just append "-e" to "-IAAR-RAAI"

#for i in {1864..1907}
for i in {1864..1966}
do
	wget "http://central.bac-lac.gc.ca/.item/?id="$i"-IAAR-RAAI&op=pdf&app=indianaffairs"
done
