#!/bin/bash
FILEPATH=~/vejcobus-statistics/datapoints

FILES=$(ls $FILEPATH -t)
if [ $# -ge 1 ]
then
	FILES=$(grep $1 <<< "$FILES")
fi
if [ -z "$FILES" ]
then 
	echo "ERROR: No matching file found"
	exit 1
fi
FILE=$(head -1 <<< "$FILES")

FILEPATH=$FILEPATH/$FILE
FILESIZE=$(echo "scale=2; $(wc -c < $FILEPATH) / 1024" | bc)

echo $FILE $FILESIZE kilobytes $(wc -l < $FILEPATH) lines
echo
tail -1 $FILEPATH
