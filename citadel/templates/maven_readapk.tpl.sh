AAPT_TOOL="$ANDROID_HOME/build-tools/$(ls -rt $ANDROID_HOME/build-tools | tail -1)/aapt"
VERSION=$($AAPT_TOOL d badging "{artifact}" | grep versionName | awk -F\' '{{print $4"-"$6}}')
