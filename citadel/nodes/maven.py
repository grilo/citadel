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

        # Always display maven's version
        mvn_exec = citadel.tools.get_executable('mvn') + ' -V -B'
        logging.debug('Found maven executable: %s', mvn_exec)

        if 'build' in path:

            yml = self.set_defaults(yml, {
                'pom': 'pom.xml',
                'lifecycle': 'clean install',
                'opts': '',
            })

            validated = self.validate(yml, [
                'pom',
                'lifecycle',
                'opts',
            ])

            for k in validated.keys():
                del yml[k]

            cmd = ['%s -f "%s" %s %s' % (mvn_exec, validated['pom'], validated['lifecycle'], validated['opts'])]
            for k, v in yml.items():
                cmd.append('-D%s=%s' % (k, v))
            self.output.append(self.format_cmd(cmd))

        elif 'publish' in path:

            yml = self.set_defaults(yml, {
                'opts': '',
                'version': '${VERSION}',
                'snapshot': False,
            })

            validated = self.validate(yml, [
                'file',
                'artifactId',
                'groupId',
                'version',
                'snapshot',
                'opts',
            ])

            for k in validated.keys():
                del yml[k]

            if validated['version'] == '${VERSION}':
                version = citadel.tools.get_version(validated['file'], validated)
                if not version:
                    self.add_error('Unable to automatically induce version for: %s' % (validated['file']))
                self.output.append(version)

            if validated['snapshot']:
                validated['version'] += '-SNAPSHOT'

            cmd = ['%s deploy:deploy-file %s' % (mvn_exec, validated['opts'])]
            for k, v in validated.items():
                cmd.append('-D%s="%s"' % (k, v))          

            for k, v in yml.items():
                cmd.append('-D%s="%s"' % (k, v))
            self.output.append(self.format_cmd(cmd))
