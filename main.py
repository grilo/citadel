#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Some description."""

import logging
import argparse
import sys
import collections
import os
import subprocess
import shlex
import re
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

def filter_secrets(lines):
    filtered = []
    for line in lines:
        if re.search('.*password.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(password[\s:=]+)([\'"]*\w[\'"]*).*', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        elif re.search('.*secret.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(secret[\s:=]+)([\'"]*\w[\'"]*)*.*', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        else:
            filtered.append(line)
    return filtered


def main():

    desc = 'Generate a shell script that runs a build.'
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-v", "--verbose", action="store_true", \
        help="Increase output verbosity")
    parser.add_argument("-f", "--file", default="citadel.yml", \
        help="A YAML file used to generate the build script.")
    parser.add_argument("-n", "--validate-only", action="store_true", \
        help="Validate only, exit with error code 1 if any errors are found.")
    parser.add_argument("-e", "--environment", default='', \
        help="Set the execution environment.")
    parser.add_argument("-x", "--execute", action="store_true", \
        help="Execute the bash file after generating it.")

    args = parser.parse_args()

    logging.basicConfig(format=settings.log_format)
    logging.getLogger().setLevel(getattr(logging, settings.log_level.upper()))
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if os.path.isdir(args.file):
        args.file = os.path.join(args.file, 'citadel.yml')
    else:
        args.file = os.path.join('.', args.file)

    with open(args.file) as yml_file:
        old_cwd = os.getcwd()
        os.chdir(os.path.dirname(args.file))

        ordered_yml = ordered_load(yml_file, extlibs.yaml.SafeLoader)
        builder = nodes.root.Node(ordered_yml, [], args.environment)
        errors = builder.get_errors()

        if len(errors) > 0:
            logging.critical("Found (%d) errors while parsing: %s" % (len(errors), args.file))
            for e in errors:
                logging.critical(e)
            sys.exit(1)
        if args.validate_only:
            logging.info("Validation mode only, exiting...")
            sys.exit(0)

        output = "\n".join(filter_secrets(builder.to_bash()))
        logging.debug('Generated script:\n%s' % (output))

        if args.execute:
            with open(os.path.basename(args.file) + '.sh', 'w') as sh_file:
                sh_file.write(output)
                sh_file.close()
                cmd = 'bash ' + sh_file.name
                logging.info("Executing: %s" % (cmd))
                proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                while True:
                    line = proc.stdout.readline()
                    if line == '' and proc.poll() is not None:
                        break
                    sys.stdout.write(line)
                    sys.stdout.flush()
                sys.exit(proc.returncode)
        os.chdir(old_cwd)

if __name__ == '__main__':
    main()
