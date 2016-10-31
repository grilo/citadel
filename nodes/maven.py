#!/usr/bin/env python

import zipfile
import logging
import os
import glob

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

        if 'build' in path:
            pom = 'pom.xml'
            lifecycle = 'clean install'
            opts = ''
            if 'lifecycle' in yml.keys():
                lifecycle = yml['lifecycle']
                del yml['lifecycle']
            else:
                self.add_error('Building with maven requires "lifecycle" to be specified.')
            if 'pom' in yml.keys():
                pom = yml['pom']
                del yml['pom']
            else:
                logging.debug('No "build/maven/pom" detected, defaulting to: %s' % (pom))

            if 'opts' in yml.keys():
                opts = yml['opts']
                del yml['opts']

            cmd = ['%s -f "%s" %s %s' % (mvn_exec, pom, lifecycle, opts)]
            for k, v in yml.items():
                cmd.append('-D%s=%s' % (k, v))
            self.output.append(self.format_cmd(cmd))

        elif 'publish' in path:
            if not 'file' in yml.keys():
                self.add_error('Publishing with maven requires "file" to be specified.')
                return
            if not os.access(yml['file'], os.R_OK):
                self.add_error('Unable to publish unreadable file: %s' % (yml['file']))
                return
            cmd = ['%s deploy:deploy-file' % (mvn_exec)]
            if not 'version' in yml.keys():
                yml['version'] = self.detect_version(yml['file'])
            if not yml['version']:
                self.add_error('Unable automatically detect version for maven publishing.')
            for k, v in yml.items():
                cmd.append('-D%s=%s' % (k, v))
            self.output.append(self.format_cmd(cmd))

    def detect_version(self, file):
        version = None
        if file.endswith('.apk'):
            version = self.read_apk_version(file)
        elif file.endswith('.jar') or file.endswith('.war') or file.endswith('.ear'):
            version = self.read_jar_version(file)
        return version

    def read_apk_version(self, file):
        if 'ANDROID_HOME' in os.environ and os.access(os.path.join, os.X_OK):
            build_tools = os.path.join(os.environ['ANDROID_HOME'], 'build_tools')
            latest = max(glob.glob(os.path.join(build_tools, '*/')), key=os.path.getmtime)
            aapt_tool = os.path.join(build_tools, aapt_tool, 'appt')
            rc, out = self.run_cmd([aapt_tool + 'dump badging ' + file])
            for line in out.splitlines():
                if 'versionName' in line:
                    tokens = line.split()
                    return tokens[4] + '-' + tokens[6]
        return None

    def read_jar_version(self, file):
		with zipfile.ZipFile(file, "r") as jar:
			for zipinfo in jar.infolist():
				if zipinfo.filename.endswith('pom.properties'):
					for line in jar.open(zipinfo).read().splitlines():
						if line.startswith('version='):
							return line.split('=', 1)[-1]
		return None
