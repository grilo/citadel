#!/usr/bin/env python

import logging

import citadel.nodes.root
import citadel.tools


class Maven(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Maven, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        if 'build' in path:
            self.defaults = {
                'pom': 'pom.xml',
                'lifecycle': 'clean install',
                'opts': '',
            }
            self.requirements = [
                'pom',
                'lifecycle',
                'opts',
            ]

        elif 'publish' in path:
            self.defaults = {
                'opts': '',
                'version': '${VERSION}',
                'snapshot': False,
            }
            self.requirements = [
                'file',
                'artifactId',
                'groupId',
                'version',
                'snapshot',
                'opts',
            ]

    def to_bash_build(self):
        mvn_exec = citadel.tools.get_executable('mvn') + ' -V -B'

        cmd = ['%s -f "%s" %s %s' % (mvn_exec, self.yml['pom'], self.yml['lifecycle'], self.yml['opts'])]
        for k in self.requirements:
            del self.yml[k]
        for k, v in self.yml.items():
            cmd.append('-D%s=%s' % (k, v))
        return self.format_cmd(cmd)

    def to_bash_publish(self):
        mvn_exec = citadel.tools.get_executable('mvn') + ' -V -B'
        version = ''
        if self.yml['version'] == '${VERSION}':
            version = citadel.tools.read_jar_version(self.yml['file'], self.yml['groupId'], self.yml['artifactId'])

        if self.yml['snapshot']:
            self.yml['version'] += '-SNAPSHOT'

        cmd = ['%s deploy:deploy-file %s' % (mvn_exec, self.yml['opts'])]

        for k in self.requirements:
            del self.yml[k]
        for k, v in self.yml.items():
            cmd.append('-D%s="%s"' % (k, v))

        for k, v in self.yml.items():
            cmd.append('-D%s="%s"' % (k, v))
        return "\n".join([
            version,
            self.format_cmd(cmd)
        ])

    def to_bash(self):
        output = []
        if 'build' in self.path:
            output.append(self.to_bash_build())
        elif 'publish' in self.path:
            output.append(self.to_bash_publish())
        return output
