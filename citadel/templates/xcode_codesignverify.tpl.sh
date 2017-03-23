unzip -oq -d "verifycodesign" "{ipafile}"
unpacked_app="$(ls verifycodesign/Payload/)"
cd verifycodesign/Payload
if ! codesign --verify --verbose=4 "$unpacked_app" --no-strict ; then
    codesign -d -r -vvvvv "$unpacked_app"
    echo "The application is not signed correctly."
    echo "This may mean out of date certificate chains, probably hidden."
    rm -fr "verifycodesign"
    exit 1
fi
cd -
rm -fr "verifycodesign"
