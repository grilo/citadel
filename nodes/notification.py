#!/usr/bin/env python

import nodes.root


class Notification(nodes.root.Node):

    def __init__(self, yml, path):
        super(Notification, self).__init__(yml, path)
