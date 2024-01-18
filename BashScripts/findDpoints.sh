# hash bang
if [ $# -lt 3 ]; then
	echo "Missing cmd arguments: day(mm-dd) [mode(W-hole/P-artial/F-ind pattern)] hour(hh) minute(mm) [timezone(z)] [direction(P-oliklinika/C-akovice]"
	exit
fi

DAY=$1
shift 1
# determine what year it is
FILE="2024-$DAY.csv"
if ! [ -f "datapoints/$FILE" ]; then
	FILE="2023-$DAY.csv"
fi

MODE=P
if [[ $1 =~ [wWpPfF] ]]; then
	MODE=${1^}
	shift 1
fi

if [ $MODE = F ]; then
	if [ $# -ge 2 ]; then
		echo "Single arg for pattern expected"
		exit 1
	fi
	PATTERN="$1"
else
	HOUR=$1
	MINUTE=$(($2+1))
	TIMEZONE=1
	DESTINATION=""
	shift 2
	# timestamp + destination
	if [ $# -ge 1 ]; then
		DIGIT_RE="^[0-9]+$"
		if [[ $1 =~ $DIGIT_RE ]]; then
			TIMEZONE=$1
			shift 1
		fi
		if [ $# -ge 1 ]; then
			DESTINATION="(Čakovice|Kbelský pivovar)"
			if [[ $1 =~ [p|P] ]]; then
				DESTINATION="Poliklinika Mazurská"
			fi
			DESTINATION="(?=.*$DESTINATION)"
			shift 1
		fi
	fi
	PATTERN="^[^,]*T0?$(($HOUR-$TIMEZONE)):0?$MINUTE:[0-9]{2}\+00:00$DESTINATION"
fi

LINES="$(grep -P "$PATTERN" datapoints/$FILE)"

if [ $MODE = W ]; then
	echo $LINES
	exit
fi

STARTS=$(grep -Eo ".+([0-9]{2}\.[0-9]+,){2}(,*[^,]+){2}|(Poliklinika Mazurská|Čakovice|Kbelský pivovar)" <<< "$LINES")
echo "$STARTS"
