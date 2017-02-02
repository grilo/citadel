#!/usr/bin/env python

import citadel.nodes.root


class Platform(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Platform, self).__init__(yml, path)
        if yml == "rhel6":
            self.output.append('if ! grep -q "Red Hat" /etc/redhat-release ; then')
            self.output.append('    echo "Requires a Red Hat system." && exit 1')
            self.output.append('fi')
        elif yml == "ubuntu":
            self.output.append('if ! grep -q "Ubuntu" /etc/issue ; then')
            self.output.append('    echo "Requires a Ubuntu system." && exit 1')
            self.output.append('fi')
