#!/usr/bin/env python

import nodes.root


class Publish(nodes.root.Node):

    def __init__(self, yml, path):
        super(Publish, self).__init__(yml, path)