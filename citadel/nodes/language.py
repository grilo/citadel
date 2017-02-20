#!/usr/bin/env python

import re

import citadel.nodes.node
import citadel.tools


class Language(citadel.nodes.node.Base):

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
