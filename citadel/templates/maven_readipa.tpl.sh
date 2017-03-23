VERSION=$(/usr/libexec/PlistBuddy \
    -c "Print ApplicationProperties::CFBundleVersion" \
    "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")
VERSION=$VERSION-$(/usr/libexec/PlistBuddy -c \
    "Print ApplicationProperties:CFBundleShortVersionString" \
    "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")
