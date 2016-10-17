#!/usr/bin/env python

import nodes.root


class Platform(nodes.root.Node):

    def __init__(self, yml, path):
        super(Platform, self).__init__(yml, path)
        self.output.append('Some test to ensure we\'re in %s' % (yml))
