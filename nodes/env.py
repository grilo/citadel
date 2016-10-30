#!/usr/bin/env python

import nodes.root


class Env(nodes.root.Node):

    def __init__(self, yml, path):
        super(Env, self).__init__(yml, path)
        self.output.append('\necho "### ENV ###"')
        for line in yml:
            self.output.append('export %s' % (line))
