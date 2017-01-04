#!/usr/bin/env python

import os

import citadel.nodes.root


class Environment(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Environment, self).__init__(yml, path)
        if not isinstance(yml, dict):
            self.add_error('Environment must be a set of Key/Value pairs and not a list')
            return

    def to_bash(self):
        output = []
        output.append('echo "### Environment ###"')
        output.append('export PWD="%s"' % (os.getcwd()))

        for k, v in self.yml.items():
            if '.' in k:
                logging.warning('Ignoring invalid export line: %s=%s', k, v)
                continue
            output.append('export %s="%s"' % (k, v))

        return output
