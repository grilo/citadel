#!/usr/bin/env python

import logging

import citadel.nodes.node
import citadel.tools


class Nodejs(citadel.nodes.node.Base):
    """:synopsis: Sets up a nodejs runtime and its native npm.

    :requirements: None
    :platform: Any

    :param node: The Node.js version to be installed.
    :type node: optional

    :param npm: The NPM version to be installed.
    :type npm: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        nodejs:
          node: v7.5.0
          npm: 3.10.7

    Sets up local nodejs and npm versions to be used across the generated
    script.

    Looks for any http client in the system (wget or curl) in the path and
    downloads the binaries from nodejs.org that correspond to the version
    in the ``node`` directive. Once nodejs is setup, it then runs an
    *npm install npm@version* and ensures both the nodejs and npm executables
    are correctly configured in the PATH.

    It will also print both the nodejs and npm versions that were configured
    into the log.

    This directive depends on a working internet connection. If any proxy
    is required, remember to specific it either in the ``environment``
    directive or directly passing the http proxy's options using the 
    ``-e "http_proxy=value"`` options through ``citadel-generate``.
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
echo "Node version: $(node --version)"
""" % (citadel.tools.find_downloader(), version)

    def install_npm(self, version):
        return """
NPM_VERSION="%s"
if ! which npm ; then
    echo "At least one npm version must be installed to boostrap any further npm installations."
    exit 1
fi
npm install npm@$NPM_VERSION
export PATH="node_modules/.bin:$PATH"
echo "NPM version: $(npm --version)" """ % (version)
