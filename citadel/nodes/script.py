#!/usr/bin/env python

import citadel.nodes.node


class Script(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Script, self).__init__(yml, path)
        self.output = yml
