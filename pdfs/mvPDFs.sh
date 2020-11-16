#!/bin/bash

for i in {1864..1966}
do
	mv "index.html?id="$i"-IAAR-RAAI&op=pdf&app=indianaffairs" $i"-IAAR-RAAI.pdf"
done
