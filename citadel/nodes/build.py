#!/usr/bin/env python

import nodes.root


class Build(nodes.root.Node):

    def __init__(self, yml, path):
        super(Build, self).__init__(yml, path)
        self.output.append('\necho "### Build ###"')
