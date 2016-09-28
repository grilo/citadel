#!/usr/bin/env python

import nodes.root


class Build(nodes.root.Node):

    def __init__(self, yml):
        super(Build, self).__init__(yml)
