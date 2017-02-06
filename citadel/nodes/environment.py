#!/usr/bin/env python

import citadel.nodes.node


class Environment(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Environment, self).__init__(yml, path)
        self.output.append('\necho "### Environment Variables ###"')
        if isinstance(yml, list):
            for line in yml:
                self.output.append('export %s' % (line))
        elif isinstance(yml, dict):
            for k, v in yml.items():
                self.output.append('export %s=%s' % (k, v))
