#!/usr/bin/env python

import nodes.root


class Test(nodes.root.Node):

    def __init__(self, yml, path):
        super(Test, self).__init__(yml, path)
