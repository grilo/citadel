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
        logging.debug('Loading (%s): %s' % (self.__class__.__name__, "/".join(path)))
        self.errors = []
        self.output = []
        self.children = []
        self._parse_children(yml)
        if not path and self.__class__.__name__ == 'Node':
            self.output.append('#!/usr/bin/env bash')
            self.output.append('\n### Automagically generated ###\n')
            self.output.append('set -eu')
            self.output.append('set -o pipefail\n')

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
        if isinstance(yml, list):
            for i in yml:
                self._parse_children(i)
        if not isinstance(yml, dict):
            return
        for k in yml.keys():
            try:
                class_instance = self.__load_plugin(k, os.path.join('nodes', k + '.py'))
                self.children.append(class_instance(yml[k], self.path + [k]))
            except NotImplementedError:
                pass

    def add_error(self, msg):
        self.errors.append('%s: %s' % ("/".join(self.path), msg))

    def format_cmd(self, command_list):
        return " \ \n    ".join(command_list)

    def get_errors(self):
        for child in self.children:
            self.errors.extend(child.get_errors())
        return self.errors

    def to_bash(self):
        for child in self.children:
            self.output.extend(child.to_bash())
        return self.output
