#!/usr/bin/env python

import logging
import os

import citadel.nodes.node
import citadel.tools


class Rbenv(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Rbenv, self).__init__(yml, path)

        if 'ruby' in self.yml.keys():
            logging.info('Detected ruby version request: %s', self.yml['ruby'])
            out = self.rbenv(self.yml['ruby'])
            self.output.append(out)

        if 'cocoapods' in self.yml.keys():
            logging.info('Detected cocoapods version request: %s', self.yml['cocoapods'])
            out = self.cocoapods(self.yml['cocoapods'])
            self.output.append(out)

    def rbenv(self, ruby_version):
        return """export RBENV_VERSION="%s"
export RBENV_DIR=$HOME/.rbenv
export RUBY_CONFIGURE_OPTS="--disable-install-doc"
if which rvm ; then
    echo "yes" | rvm implode
fi

if [ ! -d "$RBENV_DIR" ] ; then
    git clone https://github.com/rbenv/rbenv.git "$RBENV_DIR"
else
    cd "$RBENV_DIR"
    git pull
    cd -
fi

if [ ! -d "$RBENV_DIR/plugins/ruby-build" ] ; then
    git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
else
    cd "$RBENV_DIR/plugins/ruby-build"
    git pull
    cd -
fi

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

if ! rbenv versions | grep "$RBENV_VERSION" ; then
    echo "This might take a few minutes..."
    rbenv install $RBENV_VERSION
fi""" % (ruby_version)

    def cocoapods(self, cocoapods_version):
        return """VERSION="%s"
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
pod _${VERSION}_ install --verbose""" % (cocoapods_version)

