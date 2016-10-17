#!/usr/bin/env python

import nodes.root


class Mail(nodes.root.Node):

    def __init__(self, yml, path):
        super(Mail, self).__init__(yml, path)
