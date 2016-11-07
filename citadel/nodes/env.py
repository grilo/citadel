#!/usr/bin/env python

import citadel.nodes.root


class Env(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Env, self).__init__(yml, path)
        self.output.append('\necho "### ENV ###"')
        for line in yml:
            self.output.append('export %s' % (line))
