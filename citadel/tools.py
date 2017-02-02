#!/usr/bin/env python

import zipfile
import glob
import os
import subprocess
import shlex
import distutils.spawn
import plistlib
import collections
import re
import plistlib
import logging

import citadel.yaml


def run_cmd(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout

def get_executable(executable):
    # Not sure if this is python3 compatible
    return distutils.spawn.find_executable(executable)

def get_branch_name(directory):
    branch_name = None
    old_dir = os.getcwd()
    os.chdir(directory)
    # Git
    rc, out = tools.run_cmd('git rev-parse --abbrev-ref HEAD')
    if rc == 0:
        branch_name = out.strip()
        logging.debug('Git repo detected. Branch: %s' % (branch_name))
    # AccuRev
    rc, out = tools.run_cmd('accurev info')
    if rc == 0:
        lines = [line for line in out.splitlines() if line.strip().startswith('Basis')]
        branch_name = lines[0].split(": ")[-1]
        logging.debug('AccuRev repo detected: %s' % (branch_name))

    os.chdir(old_dir)
    return branch_name

def ordered_load(stream, Loader=citadel.yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        citadel.yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return citadel.yaml.load(stream, OrderedLoader)

def filter_secrets(lines):
    filtered = []
    for line in lines:
        if re.search('.*password.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(password[\s:=]+)([\'"]*.*[\'"]*)[\s$].*', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        elif re.search('.*secret.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(secret[\s:=]+)([\'"]*.*[\'"]*)[\s$]', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        else:
            filtered.append(line)
    return filtered

def find_file(wildcard):
    dirname = os.path.dirname(wildcard)
    if not dirname:
        dirname = '.'
    filename = os.path.basename(wildcard)
    return '\n'.join([
        'FILE=$(find %s -type f -name "%s")' % (dirname, filename),
        'if [ $(echo "$FILE"  | wc -l) -gt 1 ] ; then',
        '    echo "Too many results found while looking for %s. Aborting..." && exit 1' % (wildcard),
        'fi',
    ])

def bash_syntax(string):
    if not string:
        return False
    try:
        subprocess.check_call("echo '%s' | bash -n" % (string), shell=True)
        return True
    except:
        return False
