#!/usr/bin/env python

import citadel.nodes.root


class Deploy(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Deploy, self).__init__(yml, path)

    def to_bash(self):
        return ['\necho "### Deploy ###"']
