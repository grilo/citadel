#!/usr/bin/env python

import re

import citadel.nodes.node
import citadel.tools


class Language(citadel.nodes.node.Base):
    """:synopsis: Sets a required language/runtime for the environment.

    :requirements: None
    :platform: Any

    :param language: The language for the build environment.
    :type language: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        language: java1.8

    Supported languages are:
	# java
	# npm (javascript)
	# xcode (objective C/swift)

	The language should be specified with a number. Examples below:

    .. code-block:: yaml
        :linenos:

		language: npm2.6
		language: java1.8
		language: java7
		xcode: 8.1

	Depending on the language choice, the heuristic will be different. For Java,
	the "alternatives" command will be used (incompatible with OSX and Windows).
	For npm, the binary will be looked for in the PATH (which command). For
	Xcode, the "xcode-select" command will be used with the following arguments:

    .. code-block:: bash
        :linenos:

        sudo xcode-select -s /Applications/Xcode%s.app' % (wanted_version)

	This means that this module's platform support is extremely limited and
	should be used with care.
    """

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)
        self.parse_lang(yml)

    def parse_lang(self, lang):
        if 'java' in lang:
            javac = None
            version = re.search(r'[0-9\.]+', lang).group(0)
            for alt in self.get_alternatives('javac'):
                if 'javac' in alt and 'java-' + version in alt:
                    javac = alt
            if not javac:
                self.add_error('Unsupported language (%s).' % (lang))
                return

            java_home = javac.split("/bin/javac")[0]
            self.output.append('export JAVA_HOME="%s"' % (java_home))
        elif 'npm' in lang:
            wanted_version = re.match(r'npm([0-9\.]+)', lang).group(1)
            npm = citadel.tools.find_executable('npm')
            rc, out = citadel.tools.run_cmd(npm + ' --version')
            existing_version = out.strip()
            if not re.match(wanted_version, existing_version):
                self.add_error('Couldn\'t find the required npm version (%s).' % (wanted_version))
        elif 'xcode' in lang:
            wanted_version = re.match(r'xcode([A-Za-z0-9\.\-]+)', lang).group(1)
            self.output.append('sudo xcode-select -s /Applications/Xcode%s.app' % (wanted_version))

    def get_alternatives(self, binary):
        try:
            rc, out = citadel.tools.run_cmd('update-alternatives --list %s' % (binary))
            if rc == 2:
                rc, out = citadel.tools.run_cmd('update-alternatives --display %s' % (binary))
                outlines = []
                for line in out.splitlines():
                    if line.startswith('/'):
                        outlines.append(re.sub(r' - .*', '', line))
                out = "\n".join(outlines)
        except OSError:
            rc, out = citadel.tools.run_cmd('/usr/sbin/update-alternatives --display %s' % (binary))
            outlines = []
            for line in out.splitlines():
                if line.startswith('/'):
                    outlines.append(re.sub(r' - .*', '', line))
            out = "\n".join(outlines)
        return out.splitlines()
