#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools


class Gradle(citadel.nodes.node.Base):
    """:synopsis: Run gradle for builds.

    :requirements: None
    :platform: Any

    :param lifecycle: The lifecycle stages to be run (default: clean assemble).
    :type lifecycle: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
          gradle:
            lifecycle: clean assemble
            httpProxy: 127.0.0.1

    Apart from the lifecycle, all the unrecognized options will be translated \
	into ``-Doption=value``.

	As such, the above statement would become.

    .. code-block:: bash
        :linenos:

        gradle clean assemble -DhttpProxy=127.0.0.1


    If 'gradle' isn't found in the PATH (tested using a which command), then
    the gradle wrapper will be used (a ``gradlew`` executable file must exist
    at the root of the project).
    """

    def __init__(self, yml, path):
        super(Gradle, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        self.output.append(citadel.tools.template('gradle_getgradle'))
        gradle_exec = '"$GRADLE_EXEC"'

        if 'build' in path:

            self.parser.add_default('lifecycle', 'clean assemble')

            errors, parsed, ignored = self.parser.validate()

            cmd = ['%s' % (gradle_exec)]
            cmd.append(parsed['lifecycle'])

            for key, value in ignored.items():
                cmd.append('-D%s="%s"' % (key, value))
            self.output.append(citadel.tools.format_cmd(cmd))
