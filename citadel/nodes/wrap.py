#!/usr/bin/env python

import citadel.nodes.node

class Wrap(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Wrap, self).__init__(yml, path)
