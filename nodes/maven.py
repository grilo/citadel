#!/usr/bin/env python

import logging
import distutils.spawn

import nodes.root


class Maven(nodes.root.Node):

    def __init__(self, yml, path):
        super(Maven, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        # Unsure if this is python3 compatible
        # Always display maven's version
        mvn_exec = self.get_executable('mvn') + ' -V'

        if path[-2] == 'build':
            self.output.append(mvn_exec + ' ' + yml)

        elif path[-2] == 'publish':
            if not 'file' in yml.keys():
                self.add_error('Publishing with maven requires "file" to be specified.')
            cmd = ['%s deploy:deploy-file' % (mvn_exec)]
            for k, v in yml.items():
                cmd.append('-D%s=%s' % (k, v))
            self.output.append(self.format_cmd(cmd))
