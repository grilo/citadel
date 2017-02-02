#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some description."""

import logging
import os

import citadel.yaml
import citadel.tools
import citadel.nodes.root


def load(yml_file, environment, ignore):


    with open(yml_file) as fd:
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(yml_file))

        ordered_yml = citadel.tools.ordered_load(fd, citadel.yaml.SafeLoader)

        builder = citadel.nodes.root.Node(ordered_yml, [], environment, ignore)
        errors = builder.get_errors()

        if len(errors) > 0:
            logging.critical("Found (%d) errors while parsing: %s" % (len(errors), yml_file))
            for e in errors:
                logging.critical(e)
            os.chdir(old_cwd)
            return False

        output = builder.to_bash()
        logging.debug('Generated script:\n%s' % ('\n'.join(citadel.tools.filter_secrets(output))))

        os.chdir(old_cwd)
        return '\n'.join(output)
