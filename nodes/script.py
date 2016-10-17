#!/usr/bin/env python

import nodes.root


class Script(nodes.root.Node):

    def __init__(self, yml, path):
        super(Script, self).__init__(yml, path)
        self.output = yml
