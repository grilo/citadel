#!/usr/bin/env python

import logging

import citadel.nodes.root
import citadel.tools


class Nodejs(citadel.nodes.root.Node):
    """

        nodejs:
          node: v7.5.0
          npm: 3.10.7

    """

    def __init__(self, yml, path):
        super(Nodejs, self).__init__(yml, path)

        if 'node' in self.yml.keys():
            out = self.install_node(self.yml['node'])
            self.output.append(out)

        if 'npm' in self.yml.keys():
            out = self.install_npm(self.yml['npm'])
            self.output.append(out)

    def install_node(self, version):
        return """%s
NODE_VERSION="%s"
[ ! -f "node-${NODE_VERSION}-linux-x64.tar.gz" ] || rm -f node-${NODE_VERSION}-linux-x64.tar.gz
${DOWNLOADER} https://nodejs.org/download/release/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.gz
[ ! -d "node-${NODE_VERSION}-linux-x64.tar.gz" ] || rm -fr node-${NODE_VERSION}-linux-x64.tar.gz
tar -xzf node-${NODE_VERSION}-linux-x64.tar.gz
rm -f node-${NODE_VERSION}-linux-x64.tar.gz
export PATH="node-${NODE_VERSION}-linux-x64/bin:$PATH"
node --version
""" % (citadel.tools.find_downloader(), version)
        pass

    def install_npm(self, version):
        return """
NPM_VERSION="%s"
if ! which npm ; then
    echo "At least one npm version must be installed to boostrap any further npm installations."
    exit 1
fi
npm install npm@$NPM_VERSION
export PATH="node_modules/.bin:$PATH"
npm --version""" % (version)
