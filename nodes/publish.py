#!/usr/bin/env python

import nodes.root


class Publish(nodes.root.Node):

    def __init__(self, yml):
        super(Publish, self).__init__(yml)

    def to_bash(self):
        output = []
        for pkg in self.yml['publish']:
            if pkg.keys()[0] == 'maven':
                output.append('mvn deploy')
            elif pkg.keys()[0] == 'npm':
                output.append('npm publish')
        return output
