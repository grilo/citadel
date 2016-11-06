#!/usr/bin/env python

import logging
import os

import nodes.root
import tools


class Branch(nodes.root.Node):

    def __init__(self, yml, path):
        """Conditional execution based on branch name."""
        if self.get_branch_name() == yml['name']:
            super(Branch, self).__init__(yml, path)
        else:
            # Since we've prevented our recursive stuff to go on, 
            # we need to do our own init and pretend we're the real
            # deal.
            self.children = []
            self.errors = []
            self.output = []
            logging.debug('Skipping since it doesn\'t match branch name.')

    def get_branch_name(self):
        branch_name = None

        # Git
        rc, out = tools.run_cmd('git rev-parse --abbrev-ref HEAD')
        if rc == 0:
            branch_name = out.strip()
            logging.debug('Git repo detected. Branch: %s' % (branch_name))

        # AccuRev
        rc, out = tools.run_cmd('accurev info')
        if rc == 0:
            for line in out.splitlines():
                if line.strip().startswith('Workspace/Ref'):
                    ws = line.split(": ")[-1]
                    rc, basis = tools.run_cmd('accurev show -s %s streams' % (ws))
                    branch_name = basis.splitlines()[-1].split()[1].strip()
                    logging.debug('AccuRev repo detected: %s' % (branch_name))
                    break

        return branch_name
