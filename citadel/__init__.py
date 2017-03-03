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


    with open(yml_file) as yml_fd:
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(yml_file))
        logging.info('Switched execution directory to: %s', os.getcwd())

        ordered_yml = citadel.tools.ordered_load(yml_fd, citadel.yaml.SafeLoader)

        tree_builder = citadel.tree.Builder(ignore)
        root_node = tree_builder.build(ordered_yml, environment)

        tree_walker = citadel.tree.Walker()
        errors = tree_walker.get_errors(root_node)

        if len(errors) > 0:
            logging.critical("Found (%d) errors while parsing: %s", len(errors), yml_file)
            for error in errors:
                logging.critical(error)
            os.chdir(old_cwd)
            return False

        output = tree_walker.get_output(root_node)
        logging.debug('Generated script:\n%s', '\n'.join(citadel.tools.filter_secrets(output)))

        os.chdir(old_cwd)
        return '\n'.join(output)
