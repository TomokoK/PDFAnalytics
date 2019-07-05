#!/bin/bash

for i in {1864..1907}
do
	wget "http://central.bac-lac.gc.ca/.item/?id="$i"-IAAR-RAAI&op=pdf&app=indianaffairs"
done
