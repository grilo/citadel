#!/usr/bin/env python

import os
import sys
import inspect
import logging
import extlibs.yaml


class Node(object):

    def __init__(self, yml, path=[]):
        self.yml = yml
        self.path = path
        self.errors = 0
        self.output = []
        self.children = []
        if isinstance(yml, dict):
            self._parse_children(yml)

    def __load_plugin(self, name, path):
        directory = os.path.dirname(path)
        sys.path.append(directory)
        try:
            module = __import__(name, globals(), locals(), [], -1)
        except SyntaxError as e:
            raise e
        except ImportError as e:
            pass
        try:
            module = __import__(name, globals(), locals(), [], -1)
            class_instance = getattr(module, name.capitalize())
            del sys.path[-1]
            return class_instance
        except:
            raise NotImplementedError("Unable to find requested module in path: %s" % (path))

    def _parse_children(self, yml):
        for k in yml.keys():
            try:
                class_instance = self.__load_plugin(k, os.path.join('nodes', k + '.py'))
                self.children.append(class_instance(yml[k], self.path + [k]))
            except NotImplementedError:
                pass

    def get_errors(self):
        for child in self.children:
            self.errors += child.get_errors()
        return self.errors

    def to_bash(self):
        for child in self.children:
            self.output.extend(child.to_bash())
            self.output.append("\n# end " + child.__class__.__name__.lower())
        return self.output
