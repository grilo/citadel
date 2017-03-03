#!/usr/bin/env python

"""Tree builder and walker.

Very basic implementation used to construct a tree of CITADel nodes. These
nodes will generate output which will then get walked and collected into
one big string."""

import os
import sys
import logging

import citadel.tools


class Builder(object):
    """Build a tree of CITADel nodes."""

    def __init__(self, ignore=[]):
        self.ignore = ignore
        self.basedir = sys.path[0]

    def create_node(self, name, yml, path=[]):
        """Create a CITADel node.

        Import the python module corresponding to 'name' and pass the entire
        yml string to its constructor. The instanced object is responsible for
        handling the string correctly."""

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
        """Bootstrap root node creation, prepare and execute recursive call."""
        root_path = os.path.join(self.basedir, 'citadel', 'nodes', 'root.py')
        instance = citadel.tools.load_module('root', root_path)
        root = instance(yml, [], environment)
        # Prime the tree generation
        root.children = self.build_tree(yml, [])
        return root

    def build_tree(self, yml, path):
        """Recursively traverse the dict (yml)."""

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
                    logging.warning('Skipping all fraternal nodes because of: %s',
                                    '/'.join(path + [k]))
                    return []
                else:
                    nodes.append(node)
                    node.children.extend(self.build_tree(yml[k], path + [k]))
            except NotImplementedError:
                if isinstance(yml[k], dict):
                    logging.debug('Unknown module: %s. Ignoring it and all its descendants.', k)

        return nodes


class Walker(object):
    """Simple tree walker."""

    def __init__(self):
        pass

    def walk(self, node):
        """Convert a tree into a flat sequence of nodes."""
        nodes = []
        for child in node.children:
            nodes.append(child)
            nodes.extend(self.walk(child))
        return nodes

    def get_errors(self, root_node):
        """Collect all the errors."""
        errors = root_node.errors
        for node in self.walk(root_node):
            errors.extend(node.errors)
        return errors

    def get_output(self, root_node):
        """Collect the generated output."""
        output = root_node.output
        for node in self.walk(root_node):
            output.extend(node.output)
        return output
