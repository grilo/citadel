#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some description."""

import logging
import os

import citadel.yaml
import citadel.tools
import citadel.tree


def load(yml_file, environment, ignore):
    """Load the YML file."""


    with open(yml_file) as fd:
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(yml_file))

        ordered_yml = citadel.tools.ordered_load(fd, citadel.yaml.SafeLoader)

        b = citadel.tree.Builder(ignore)
        root_node = b.build(ordered_yml, environment)

        w = citadel.tree.Walker()
        errors = w.get_errors(root_node)

        if len(errors) > 0:
            logging.critical("Found (%d) errors while parsing: %s" % (len(errors), yml_file))
            for e in errors:
                logging.critical(e)
            os.chdir(old_cwd)
            return False

        output = w.get_output(root_node)
        logging.debug('Generated script:\n%s' % ('\n'.join(citadel.tools.filter_secrets(output))))

        os.chdir(old_cwd)
        return '\n'.join(output)
