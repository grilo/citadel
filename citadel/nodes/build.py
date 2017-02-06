#!/usr/bin/env python

import citadel.nodes.node


class Build(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Build, self).__init__(yml, path)
        self.output.append('\necho "### Build ###"')
