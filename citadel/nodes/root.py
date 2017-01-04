#!/usr/bin/env python

import os
import sys
import logging


class Node(object):

    def __init__(self, yml, path=[], ignore=[]):
        logging.debug('Loading: %s', "/".join(path))
        self.yml = yml
        self.path = path
        self.ignore = ignore
        self.skip = False
        self.errors = []
        self.children = []
        self.defaults = {}
        self.requirements = []
        self._parse_children(yml)

    def __load_plugin(self, name, path):
        directory = os.path.dirname(path)
        if not directory in sys.path:
            sys.path.append(directory)
        try:
            module = __import__(name, globals(), locals(), [], -1)
            class_instance = getattr(module, name.capitalize())
            return class_instance
        except SyntaxError as e:
            raise e
        except ImportError as e:
            raise NotImplementedError("Unable to find requested module in path: %s" % (path))

    def _parse_children(self, yml):
        if isinstance(yml, list):
            for i in yml:
                self._parse_children(i)
        if not isinstance(yml, dict):
            return
        for k in yml.keys():
            if k in self.ignore:
                logging.warning('Ignoring key: %s', k)
                continue

            module_name = k
            module_path = os.path.join(sys.path[0], 'citadel', 'nodes', module_name + '.py')
            if not os.path.isfile(module_path):
                if isinstance(yml[k], dict) and 'branch' in yml[k].keys():
                    logging.debug('Found branch key within node, stage: %s', k)
                    module_name = 'stage'
                    module_path = os.path.join(sys.path[0], 'citadel', 'nodes', module_name + '.py')
                else:
                    logging.debug('Unknown module: %s', k)
                    continue

            class_instance = self.__load_plugin(module_name, module_path)
            obj = class_instance(yml[k], self.path + [k])
            if obj.skip:
                logging.warning('Skipping all fraternal nodes because of: %s', '/'.join(self.path + [k]))
                return
            obj.set_defaults()
            obj.validate()
            self.children.append(obj)

    def validate(self):
        # self.requirements (list of):
        #   'mandatory'
        #   ['at', 'least', 'one, 'of']
        #   ( 'either', 'or')
        # { 'all': '', 'or': '', 'nothing': '' }

        validated = {}

        for required in self.requirements:
            logging.info('Validating: %s/%s' % ('/'.join(self.path), required))
            if isinstance(required, str):
                if not required in self.yml.keys():
                    self.add_error('The following field is required: %s' % (required))
                else:
                    validated[required] = self.yml[required]

            elif isinstance(required, list):
                found = [k for k in self.yml.keys() if k in required]
                if not found:
                    self.add_error('At least one of the following values is required: %s' % (",".join(required)))
                else:
                    for f in found:
                        validated[f] = self.yml[f]

            elif isinstance(required, tuple):
                found = [k for k in self.yml.keys() if k in required]
                if len(found) >  1:
                    self.add_error('At most one of the following values is required: %s' % (",".join(required)))
                elif len(found) <  1:
                    self.add_error('At least one of the following values is required: %s' % (",".join(required)))
                else:
                    for f in found:
                        validated[f] = self.yml[f]

            elif isinstance(required, dict):
                found = [k for k in self.yml.keys() if k in required.keys()]
                if len(found) > 0 and len(found) != len(required.keys()):
                    self.add_error('All of the following items must be specified together: %s' % (",".join(required.keys())))
                else:
                    for f in found:
                        validated[f] = self.yml[f]

        return validated

    def set_defaults(self):
        for k, v in self.defaults.items():
            if not k in self.yml:
                self.yml[k] = v
        return self.yml

    def add_error(self, msg):
        self.errors.append('%s: %s' % ("/".join(self.path), msg))

    def format_cmd(self, command_list):
        return ' \\\n  '.join(command_list)

    def get_errors(self):
        for child in self.children:
            self.errors.extend(child.get_errors())
        return self.errors

    def to_bash(self):
        return []

    def to_string(self):
        output = self.to_bash()
        for child in self.children:
            output.extend(child.to_string())
        return output
