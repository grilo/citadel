#!/usr/bin/env python

import nodes.root


class Env(nodes.root.Node):

    def __init__(self, yml):
        super(Env, self).__init__(yml)

    def to_bash(self):
        output = []
        for line in self.yml['env']:
            output.append(line)
        return output
