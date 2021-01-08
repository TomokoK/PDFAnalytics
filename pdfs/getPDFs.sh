#!/bin/bash

# Some documents need to be designated English (see below)
# As of 2021-01-08 the following need to be manually downloaded
# 1912, 1936, 1957, 1958, 1959, 1960, 1961, 1962, 1963
# Just append "-e" to "-IAAR-RAAI"

# As of 2021-01-08 the following are missing
# 1865, 1866, 1867

for i in {1864..1966}
do
	wget "http://central.bac-lac.gc.ca/.item/?id="$i"-IAAR-RAAI&op=pdf&app=indianaffairs"
done
