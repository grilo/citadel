#!/usr/bin/env python

import logging


class Node(object):

    def __init__(self, yml):
        self.data = yml

    def to_bash(self):
        logging.debug("Generating BASH output for (%s)" % (self.__class__.__name__))
        return ""
