#!/usr/bin/env python

import os
import sys
import logging
import collections

import citadel.tools


class Builder:

    def __init__(self, ignore=[]):
        self.ignore = ignore
        self.basedir = sys.path[0]

    def create_node(self, name, yml, path=[]):
        module_path = os.path.join(self.basedir, 'citadel', 'nodes', name + '.py')
        class_instance = None

        if os.path.isfile(module_path):
            class_instance = citadel.tools.load_module(name, module_path)
        elif isinstance(yml, dict) and 'branch' in yml.keys():
            logging.debug('Found branch key within node, stage: %s', name)
            class_instance = citadel.tools.load_module('stage', module_path)
        else:
            raise NotImplementedError('Unknown module: %s', name)

        return class_instance(yml, path)

    def build(self, yml, environment):
        # Bootstrap root node creation
        root_path = os.path.join(self.basedir, 'citadel', 'nodes', 'root.py')
        instance = citadel.tools.load_module('root', root_path)
        root = instance(yml, [], environment)
        # Prime the tree generation
        root.children = self.build_tree(yml, [])
        return root

    def build_tree(self, yml, path):

        nodes = []

        if isinstance(yml, list):
            for item in yml:
                nodes.extend(self.build_tree(item, path))
            return nodes
        elif not isinstance(yml, dict):
            return nodes

        for k in yml.keys():

            if k in self.ignore:
                logging.warning('Ignoring key: %s', k)
                continue

            try:
                node = self.create_node(k, yml[k], path + [k])
                if node.skip:
                    logging.warning('Skipping all fraternal nodes because of: %s', '/'.join(path + [k]))
                    return []
                else:
                    nodes.append(node)
                    node.children.extend(self.build_tree(yml[k], path + [k]))
            except NotImplementedError as e:
                if isinstance(yml[k], dict):
                    logging.debug('Unknown module: %s. Ignoring it and all its descendants.', k)

        return nodes


class Walker:

    def __init__(self):
        pass

    def walk(self, node):
        nodes = []
        for child in node.children:
            nodes.append(child)
            nodes.extend(self.walk(child))
        return nodes

    def get_errors(self, root_node):
        errors = root_node.errors
        for node in self.walk(root_node):
            errors.extend(node.errors)
        return errors

    def get_output(self, root_node):
        output = root_node.output
        for node in self.walk(root_node):
            output.extend(node.output)
        return output
