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

        gradle_exec = self.get_gradle()
        parser = citadel.parser.Options(self.yml)

        if 'build' in path:

            parser.add_default('lifecycle', 'clean assemble')

            errors, parsed, ignored = parser.validate()

            cmd = ['%s' % (gradle_exec)]
            cmd.append(parsed['lifecycle'])

            for k, v in ignored.items():
                cmd.append('-D%s="%s"' % (k, v))
            self.output.append(self.format_cmd(cmd))

    def get_gradle(self):
        self.output.append("""GRADLE="$(which gradle)"
if [ -z "${GRADLE}" ] ; then
    echo "Unable to find gradle in $PATH, using default wrapper."
    GRADLE="./gradlew"
fi
$GRADLE --version
""")
        return "$GRADLE"
