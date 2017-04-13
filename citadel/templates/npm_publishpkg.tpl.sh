filelist=$(find {directory} -maxdepth 1 -name "{wildcard}" | sort | grep -v "^{directory}$")
npmregistry="{registry}"
if [ $(echo "$filelist" | wc -l) -eq 0 ] ; then
    echo "Unable to find any packages to publish!"
else
    cmd="npm $npmregistry"
    scope="{scope}"
    if [ ! -z "$scope" ] ; then
        cmd="$cmd --scope $scope"
    fi
    for pkg in $filelist ; do
        $cmd publish $pkg
    done
fi
