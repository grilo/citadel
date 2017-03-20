#!/usr/bin/env python

import logging
import re
import os
import xml.etree.cElementTree as et
import abc
import sys

import citadel.tools


class SCMClient(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass
    @abc.abstractmethod
    def get_active_branch(self):
        pass
    @abc.abstractmethod
    def get_active_files(self):
        pass
    @abc.abstractmethod
    def get_active_issues(self):
        pass

class AccuRev(SCMClient):

    def __init__(self):
        super(AccuRev, self).__init__()

    def get_active_branch(self):
        branch_name = ''
        rc, out = citadel.tools.run_cmd('accurev info')
        for line in out.splitlines():
            if line.strip().startswith('Basis'):
                branch_name = line.split(":")[-1].strip()
        if not branch_name:
            logging.warning('Unable to detect any branch name in the current directory.')
        return branch_name

    def get_active_files(self):
        branch = self.get_active_branch()
        rc, out = citadel.tools.run_cmd('accurev stat -s %s -d -fl' % (branch))
        changed_files = []
        for line in out.splitlines():
            if line == '':
                continue
            changed_files.append(line)
        return '\n'.join(changed_files)

    def get_active_issues(self):
        branch = self.get_active_branch()
        stream_issues = []
        # Need to run with both -i and without -i
        rc, out = citadel.tools.run_cmd('accurev issuelist -s %s -fx -p ING' % (branch))
        xml = et.fromstring(out)
        for issue in xml[0].findall("./issue"):
            stream_issues.append(issue.find('IDNotes').text)
        rc, out = citadel.tools.run_cmd('accurev issuelist -i -s %s -fx -p ING' % (branch))
        xml = et.fromstring(out)
        for issue in xml[0].findall("./issue"):
            if issue.find('IDNotes').text.upper().startswith('STRY'):
                stream_issues.append(issue.find('IDNotes').text)
        logging.debug('Issues found in (%s): %s', branch, ",".join(stream_issues))
        return ','.join(stream_issues)


class Git(SCMClient):

    def __init__(self):
        super(Git, self).__init__()

    def get_active_branch(self):
        branch_name = ''
        rc, out = citadel.tools.run_cmd('git rev-parse --abbrev-ref HEAD')
        branch_name = out.strip()
        if not branch_name:
            logging.warning('Unable to detect any branch name in the current directory.')
        return branch_name

    def get_active_files(self):
        rc, out = citadel.tools.run_cmd('git diff --name-only master')
        return out
    def get_active_issues(self):
        return ''

class NoScm:
    def __getattr__(self, name):
        logging.debug("class NoScm called with method %s" % name)
        def notImplemented(*args, **kwargs):
            return ""
        return notImplemented

def get_client(raiseOnError=True):
    # Git
    rc, out = citadel.tools.run_cmd('git status')
    if rc == 0:
        logging.debug('Git repo detected.')
        return Git()
    # AccuRev
    rc, out = citadel.tools.run_cmd('accurev info')
    if 'Workspace/ref:' in out:
        logging.debug('AccuRev repo detected.')
        return AccuRev()
    logging.warning("Cannot find type of SCM client in repo/dir: '%s'" % os.getcwd()) 
    if raiseOnError:
        raise NotImplementedError('Unknown SCM client: %s', os.getcwd())
    print NoScm()
    return NoScm()
