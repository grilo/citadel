#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some description."""

import logging
import argparse
import sys
import collections
import extlibs.yaml
import nodes.root

import settings


def ordered_load(stream, Loader=extlibs.yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        extlibs.yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return extlibs.yaml.load(stream, OrderedLoader)


def main():

    desc = 'Generate a shell script that runs a build.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-f", "--file", default="example.yml", \
        help="A YAML file used to generate the build script.")
    parser.add_argument("-n", "--validate-only", action="store_true", \
        help="Validate only, exit with error code 1 if any errors are found.")

    args = parser.parse_args()

    logging.basicConfig(format=settings.log_format)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    with open(args.file) as yml_file:
        builder = nodes.root.Node(ordered_load(yml_file, extlibs.yaml.SafeLoader))

        if builder.get_errors() > 0:
            logging.critical("Found (%d) errors while parsing: %s" % (errors, args.file))
            sys.exit(1)
        if args.validate_only:
            logging.info("Validation mode only, exiting...")
            sys.exit(0)

        print("\n".join(builder.to_bash()))


if __name__ == '__main__':
    main()
