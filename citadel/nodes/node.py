#!/usr/bin/env python

import logging

import citadel.parser


class Base(object):

    def __init__(self, yml, path=[]):
        self.yml = yml
        self.path = path
        self.skip = False
        logging.debug('Loading: %s', "/".join(path))
        self.errors = []
        self.output = []
        self.children = []
        self.parser = citadel.parser.Options(self.yml)


    def add_error(self, msg):
        self.errors.append('%s: %s' % ("/".join(self.path), msg))


class Node(Base):

    def __init__(self, yml, path):
        super(Node, self).__init__(yml, path)
