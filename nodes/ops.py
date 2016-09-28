#!/usr/bin/env python

import os
import sys
import inspect
import logging


class BashGenerator:

    def __init__(self, yml):
        self.plugins_dir = 'nodes'
        self.order = ['platform', 'env', 'build', 'publish', 'deploy', 'test', 'notification']
        self.generators = []
        self.yml = yml

    def scan_plugins(self):
        plugins = {}
        for file in os.listdir(self.plugins_dir):
            if file.startswith("__"): continue
            elif not file.endswith(".py"): continue

            true_name = ".".join(file.split(".")[:-1])
            node_plugin = os.path.join(self.plugins_dir, file)

            if os.path.isfile(node_plugin):
                try:
                    plugins[true_name] = self.__load_plugin(true_name, node_plugin)
                except AttributeError, e:
                    logging.debug("Unable to import file (%s)." % (node_plugin))
                    print(e)
        if len(plugins) <= 0:
            logging.warning("No plugins found.")
        return plugins

    def __load_plugin(self, name, path):
        directory = os.path.dirname(path)
        sys.path.append(directory)
        try:
            module = __import__(name, globals(), locals(), [], -1)
            class_instance = getattr(module, name.capitalize())
            del sys.path[-1]
            return class_instance
        except:
            logging.critical("Unable to find requested module in path: %s" % (path))
            sys.exit(1)

    def generate(self):

        self.generators = []

        for item in self.order:
            if item in self.yml.keys():
                logging.debug("Found (%s) in the parsed file." % (item))
            else: continue

            class_instance = self.__load_plugin(item, os.path.join('nodes', item + '.py'))
            self.generators.append(class_instance(self.yml))

    def get_errors(self):
        return 0

    def to_bash(self):
        string = []
        for gen in self.generators:
            string.append(gen.to_bash())
        return "\n".join(string)
