BINARY="{binary}"
BINLOCATOR="update-alternatives"

if ! which update-alternatives > /dev/null ; then
    BINLOCATOR="/usr/sbin/update-alternatives"
fi

if ! $($BINLOCATOR --list $BINARY > /dev/null 2>&1) ; then
    BINLOCATOR="$BINLOCATOR --display"
else
    BINLOCATOR="$BINLOCATOR --list"
fi

BINARY=$($BINLOCATOR $BINARY | sed 's/ - .*//g' | grep "^/.*{wildcard}")
