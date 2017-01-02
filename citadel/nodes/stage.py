#!/usr/bin/env python

import logging

import citadel.nodes.root


class Stage(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Stage, self).__init__(yml, path)
