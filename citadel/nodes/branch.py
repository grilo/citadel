#!/usr/bin/env python

import logging
import re

import citadel.nodes.node
import citadel.tools


class Branch(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        """Conditional execution based on branch name (regex match)."""
        branch_name = self.get_branch_name()
        if re.search(yml, branch_name):
            logging.debug('Matched branch name for %s: %s', '/'.join(path), branch_name)
            super(Branch, self).__init__(yml, path)
        else:
            logging.debug('Branch name mismatch for %s. Expected [%s] instead got [%s])', '/'.join(path), yml, branch_name)
            self.skip = True

    def get_branch_name(self):
        branch_name = None

        # Git
        rc, out = citadel.tools.run_cmd('git rev-parse --abbrev-ref HEAD')
        if rc == 0:
            logging.debug('Git repo detected.')
            branch_name = out.strip()

        # AccuRev
        rc, out = citadel.tools.run_cmd('accurev info')
        if rc == 0:
            logging.debug('AccuRev repo detected.')
            for line in out.splitlines():
                if line.strip().startswith('Basis'):
                    branch_name = line.split(":")[-1].strip()
                    break

        if not branch_name:
            logging.warning('Unable to detect any branch name in the current directory.')
            return ''
        logging.info('Current branch: %s', branch_name)
        return branch_name
