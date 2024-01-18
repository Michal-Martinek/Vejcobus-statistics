cd logs

FILES=$(ls | grep -E "log_[0-9]{4}-[0-9]{2}-[0-9]{2}\.txt")

for FILE in $FILES; do
	if [ -z "$(cat $FILE)" ]; then
		rm $FILE
	fi
done

ERR_FILES=$(ls -t)
if [ -z "$ERR_FILES" ]; then echo; exit; fi

echo $ERR_FILES; echo
echo $(cat $(head -1 <<< $ERR_FILES) | head -1)
