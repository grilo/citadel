#!/usr/bin/env python

import citadel.nodes.root


class Platform(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Platform, self).__init__(yml, path)

    def to_bash(self):
        output = []
        if self.yml == "rhel6":
            output.append('if ! grep -q "Red Hat" /etc/redhat-release ; then')
            output.append('    echo "Requires a Red Hat system." && exit 1')
            output.append('fi')
        elif self.yml == "ubuntu":
            output.append('if ! grep -q "Ubuntu" /etc/issue ; then')
            output.append('    echo "Requires a Ubuntu system." && exit 1')
            output.append('fi')

        return output
