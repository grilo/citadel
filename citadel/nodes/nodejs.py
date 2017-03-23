#!/usr/bin/env python

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
        """Installs nodejs from its primary location."""
        return citadel.tools.template('nodejs_installnode', {
            'downloader': citadel.tools.find_downloader(),
            'node_version': version,
        })

    def install_npm(self, version):
        """Install npm, requires an already existing NPM version.

        If node is also requested, it usually brings its own NPM as well."""
        return citadel.tools.template('nodejs_installnpm', {
            'npm_version': version
        })
