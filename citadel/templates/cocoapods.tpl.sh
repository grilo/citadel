VERSION="{cocoapods_version}"
export COCOAPODS_DISABLE_STATS="true"
if [ ! -d "$HOME/.cocoapods/repos/Old-Specs" ] ; then
    git clone https://github.com/CocoaPods/Old-Specs.git ~/.cocoapods/repos/Old-Specs
fi
if [ ! -d "$HOME/.cocoapods/repos/Specs" ] ; then
    git clone https://github.com/CocoaPods/Specs.git ~/.cocoapods/repos/Specs
fi
if [ -d "$HOME/.cocoapods/repos/master" ] ; then
    rm -fr "$HOME/.cocoapods/repos/master"
fi
if echo "${VERSION}" | grep -qi "0.3" ; then
    ln -sf "$HOME/.cocoapods/repos/Old-Specs" "$HOME/.cocoapods/repos/master"
else
    ln -sf "$HOME/.cocoapods/repos/Specs" "$HOME/.cocoapods/repos/master"
fi
rm -fr $HOME/Library/Caches/CocoaPods
gem uninstall -a -x cocoapods
gem cleanup
gem update
gem install cocoapods -v "${VERSION}"
rbenv rehash
pod _${VERSION}_ update --verbose
pod _${VERSION}_ install --verbose"""
