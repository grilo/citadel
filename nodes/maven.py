#!/usr/bin/env python

import nodes.root


class Maven(nodes.root.Node):

    def __init__(self, yml, path):
        super(Maven, self).__init__(yml, path)
