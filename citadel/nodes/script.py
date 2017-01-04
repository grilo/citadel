#!/usr/bin/env python

import citadel.nodes.root


class Script(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Script, self).__init__(yml, path)

    def to_bash(self):
        return self.yml
