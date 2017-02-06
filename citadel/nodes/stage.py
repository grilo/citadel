#!/usr/bin/env python

import logging

import citadel.nodes.node


class Stage(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Stage, self).__init__(yml, path)
