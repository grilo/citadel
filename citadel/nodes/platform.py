#!/usr/bin/env python

import nodes.root


class Platform(nodes.root.Node):

    def __init__(self, yml, path):
        super(Platform, self).__init__(yml, path)
        if yml == "rhel6":
            self.output.append('if ! grep -q "Red Hat" /etc/issue ; then')
            self.output.append('    echo "This is only expected to work in a Red Hat system." && exit 1')
            self.output.append('fi')
        elif yml == "ubuntu":
            self.output.append('if ! grep -q "Ubuntu" /etc/issue ; then')
            self.output.append('    echo "This is only expected to work in a Ubuntu system." && exit 1')
            self.output.append('fi')
