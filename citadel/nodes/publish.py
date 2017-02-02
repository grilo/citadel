#!/usr/bin/env python

import citadel.nodes.root


class Publish(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Publish, self).__init__(yml, path)
