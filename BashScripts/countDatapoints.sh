cd datapoints
FILES=$(find . -name '*.csv' | sort -n)

COUNTS=$(xargs wc -l <<< $FILES)

if [ $# -ge 1 ]; then
	COUNTS=$(tail -$(($1+1)) <<< "$COUNTS")
fi

echo "$COUNTS"
