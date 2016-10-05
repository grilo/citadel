#!/usr/bin/env python

import nodes.root


class Build(nodes.root.Node):

    def __init__(self, yml):
        super(Build, self).__init__(yml)

    def to_bash(self):
        output = []
        for line in self.yml['build']:
            output.append(line)
        return output
