#!/usr/bin/env python

import citadel.nodes.root


class Variables(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Variables, self).__init__(yml, path)
        self.output.append('\necho "### ENVIRONMENT VARIABLES ###"')
        for line in yml:
            self.output.append('export %s' % (line))
