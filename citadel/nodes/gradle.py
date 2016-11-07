#!/usr/bin/env python

import logging

import citadel.nodes.root
import citadel.tools


class Gradle(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Gradle, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        # Unsure if this is python3 compatible
        # Always display maven's version
        gradle_exec = citadel.tools.get_executable('./gradlew')
        if not gradle_exec:
            logging.debug('Unable to find gradlew wrapper, looking in $PATH.')
            gradle_exec = citadel.tools.get_executable('gradle')
            if not gradle_exec:
                self.add_error('Unable to find neither "gradlew" nor "gradle" in $PATH.')

        if 'build' in path:

            self.output.append('%s --version' % (gradle_exec))

            cmd = ['%s' % (gradle_exec)]
            lifecycle = 'clean assemble'
            if 'lifecycle' in yml.keys():
                lifecycle = yml['lifecycle']
                del yml['lifecycle']

            cmd.append(lifecycle)

            for k, v in yml.items():
                cmd.append('-D%s="%s"' % (k, v))
            self.output.append('echo "Building..."')
            self.output.append(self.format_cmd(cmd))
