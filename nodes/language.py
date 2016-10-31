#!/usr/bin/env python

import re
import nodes.root


class Language(nodes.root.Node):

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)
        self.parse_lang(yml)

    def parse_lang(self, lang):
        if 'java' in lang:
            javac = None
            version = re.search('[0-9\.]+', lang).group(0)
            for alt in self.get_alternatives('javac'):
                if 'javac' in alt and 'java-' + version in alt:
                    javac = alt
            if not javac:
                raise Exception('Unsupported language (%s).' % (lang))

            java_home = javac.split("/bin/javac")[0]
            self.output.append('export JAVA_HOME="%s"' % (java_home))
        elif 'npm' in lang:
            wanted_version = re.match('npm([0-9\.]+)', lang).group(1)
            npm = self.get_executable('npm')
            out, rc = self.run_cmd(npm + ' --version')
            existing_version = out.strip()
            if not re.match(wanted_version, existing_version):
                self.add_error('Couldn\'t find the required npm version (%s).' % (wanted_version))
