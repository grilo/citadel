#!/usr/bin/env python

import citadel.nodes.node


class Publish(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Publish, self).__init__(yml, path)
