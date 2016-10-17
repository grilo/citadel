#!/usr/bin/env python

import nodes.root


class Npm(nodes.root.Node):

    def __init__(self, yml, path):
        super(Npm, self).__init__(yml, path)
