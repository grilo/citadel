#!/usr/bin/env python

import nodes.root


class Env(nodes.root.Node):

    def __init__(self, yml):
        super(Env, self).__init__(yml)
