echo "Xcodebuild version: $(xcodebuild -version)"
echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"

echo "ibtoold may timeout if CoreSimulator has weird stuff"
rm -fr "/Users/$(whoami)/Library/Developer/CoreSimulator"/*
echo "Build fails very often due to incorrect caching policies from Xcode (stored in DerivedData)"
rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*
