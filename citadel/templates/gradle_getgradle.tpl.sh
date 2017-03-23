GRADLE_EXEC="./gradlew"
if [ ! -f "$GRADLE_EXEC" ] ; then
    if ! which gradle > /dev/null ; then
        echo "Unable to find any gradle executable. Aborting..."
        exit 1
    fi
    echo "Unable to find gradle wrapper, using the one from PATH."
    GRADLE_EXEC="gradle"
fi
$GRADLE_EXEC --version
