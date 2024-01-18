cd datapoints
FILES=$(find . -name '*.csv' | sort -n)
xargs wc -l <<< $FILES
