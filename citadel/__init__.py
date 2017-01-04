#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some description."""

import logging
import os
import collections

import citadel.yaml
import citadel.tools
import citadel.nodes.root


def load(yml_file, environment, ignore):


    with open(yml_file) as fd:
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(yml_file))

        ordered_yml = citadel.tools.ordered_load(fd, citadel.yaml.SafeLoader)

        # Inject environment into the yaml
        if not 'environment' in ordered_yml.keys():
            ordered_yml = collections.OrderedDict([('environment', {})] + ordered_yml.items())
        elif isinstance(environment, dict):
            for line in environment.split():
                if '=' in line:
                    k, v = line.split('=', 1)
                    ordered_yml['environment'][k] = v

        # Inject header
        if not 'header' in ordered_yml.keys():
            ordered_yml = collections.OrderedDict([('header', '')] + ordered_yml.items())

        builder = citadel.nodes.root.Node(ordered_yml, [], ignore)
        errors = builder.get_errors()

        if len(errors) > 0:
            logging.critical("Found (%d) errors while parsing: %s" % (len(errors), yml_file))
            for e in errors:
                logging.critical(e)
            os.chdir(old_cwd)
            return False

        output = builder.to_string()
        logging.debug('Generated script:\n%s' % ('\n'.join(citadel.tools.filter_secrets(output))))

        os.chdir(old_cwd)
        return '\n'.join(output)
