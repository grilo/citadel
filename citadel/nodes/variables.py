#!/usr/bin/env python

import citadel.nodes.node


class Variables(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Variables, self).__init__(yml, path)
        self.output.append('\necho "### ENVIRONMENT VARIABLES ###"')
        for line in yml:
            self.output.append('export %s' % (line))
