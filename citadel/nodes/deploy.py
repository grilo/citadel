#!/usr/bin/env python

import citadel.nodes.node


class Deploy(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Deploy, self).__init__(yml, path)
        self.output.append('\necho "### Deploy ###"')
