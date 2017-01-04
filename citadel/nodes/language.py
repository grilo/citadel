#!/usr/bin/env python

import re

import citadel.nodes.root
import citadel.tools


class Language(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)

    def to_bash(self):
        lang = self.yml
        output = []

        if 'java' in lang:
            javac = None
            version = re.search(r'[0-9\.]+', lang).group(0)
            for alt in citadel.tools.get_alternatives('javac'):
                if 'javac' in alt and 'java-' + version in alt:
                    javac = alt
            if not javac:
                self.add_error('Unsupported language (%s).' % (lang))
                return []

            java_home = javac.split("/bin/javac")[0]
            output.append('export JAVA_HOME="%s"' % (java_home))
        elif 'npm' in lang:
            wanted_version = re.match(r'npm([0-9\.]+)', lang).group(1)
            npm = citadel.tools.get_executable('npm')
            rc, out = citadel.tools.run_cmd(npm + ' --version')
            existing_version = out.strip()
            if not re.match(wanted_version, existing_version):
                self.add_error('Couldn\'t find the required npm version (%s).' % (wanted_version))
        elif 'xcode' in lang:
            wanted_version = re.match(r'xcode([A-Za-z0-9\.\-]+)', lang).group(1)
            output.append('sudo xcode-select -s /Applications/Xcode%s.app' % (wanted_version))

        return output
