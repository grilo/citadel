#!/usr/bin/env python

import citadel.nodes.root


class Test(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Test, self).__init__(yml, path)
