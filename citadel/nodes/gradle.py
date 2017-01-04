#!/usr/bin/env python

import logging

import citadel.nodes.root
import citadel.tools


class Gradle(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Gradle, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')

        if not 'build' in path:
            self.add_error('Gradle currently only supports building.')

        self.defaults = {
            'lifecycle': 'clean assemble',
        }

    def to_bash(self):
        output = []

        gradle_exec = citadel.tools.get_executable('gradle')
        if not gradle_exec:
            logging.debug('Unable to find gradle in $PATH, using default wrapper.')
            gradle_exec = './gradlew'

        output.append('%s --version' % (gradle_exec))

        cmd = ['%s' % (gradle_exec)]
        cmd.append(self.yml['lifecycle'])

        del self.yml['lifecycle']

        for k, v in self.yml.items():
            cmd.append('-D%s="%s"' % (k, v))
        output.append('echo "Building..."')
        output.append(self.format_cmd(cmd))

        return output
