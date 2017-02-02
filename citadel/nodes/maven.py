#!/usr/bin/env python

import logging

import citadel.nodes.root
import citadel.tools
import citadel.parser


class Maven(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Maven, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        # Always display maven's version
        mvn_exec = citadel.tools.get_executable('mvn') + ' -V -B'
        logging.debug('Found maven executable: %s', mvn_exec)
        parser = citadel.parser.Options(self.yml)

        if 'build' in path:

            parser.add_default('pom', 'pom.xml')
            parser.add_default('lifecycle', 'clean install')
            parser.add_default('opts', '')
            errors, parsed, ignored = parser.validate()

            cmd = ['%s -f "%s" %s %s' % (mvn_exec, parsed['pom'], parsed['lifecycle'], parsed['opts'])]
            for k, v in ignored.items():
                cmd.append('-D%s=%s' % (k, v))
            self.output.append(self.format_cmd(cmd))

        elif 'publish' in path:

            parser.add_default('opts', '')
            parser.add_default('version', '${VERSION}')
            parser.add_default('snapshot', False)

            parser.is_required('file')
            parser.is_required('artifactId')
            parser.is_required('groupId')

            errors, parsed, ignored = parser.validate()
            self.errors.extend(errors)

            if parsed['file'] and parsed['version'] == '${VERSION}':

                file = parsed['file']
                version = ''

                if file.endswith('.apk'):
                    version = self.read_apk_version(file)
                elif file.endswith('.jar') or file.endswith('.war') or file.endswith('.ear'):
                    version = self.read_jar_version(file, parsed['groupId'], parsed['artifactId'])
                elif file.endswith('.ipa'):
                    version = self.read_ipa_version(file)
                else:
                    self.add_error('Unable to automatically induce version for: %s' % (parsed['file']))

                self.output.append(version)

            self.output.append(citadel.tools.find_file(parsed['file']))
            parsed['file'] = "$FILE"

            if parsed['snapshot'] and not '-SNAPSHOT' in parsed['version']:
                parsed['version'] += '-SNAPSHOT'

            cmd = ['%s deploy:deploy-file %s' % (mvn_exec, parsed['opts'])]
            for k, v in parsed.items():
                cmd.append('-D%s="%s"' % (k, v))

            for k, v in ignored.items():
                cmd.append('-D%s="%s"' % (k, v))
            self.output.append(self.format_cmd(cmd))

    def read_apk_version(self, file):
        #cmd = 'AAPT_TOOL="$ANDROID_HOME/build-tools/$(ls -rt $ANDROID_HOME/build-tools | tail -1)/aapt"\n'
        cmd = 'AAPT_TOOL="$ANDROID_HOME/build-tools/23.0.3/aapt"\n'
        cmd += 'VERSION=$($AAPT_TOOL d badging "%s" | grep versionName | awk -F\\\' \'{print $4"-"$6}\')' % (file)
        return cmd

    def read_jar_version(self, file, group_id, artifact_id):
        return "VERSION=$(unzip -p '%s' '*%s*/*%s*/pom.properties' | grep version | awk -F= '{print $2}')" % (file, group_id, artifact_id)

    def read_ipa_version(self, file):
        return """VERSION=$(/usr/libexec/PlistBuddy -c "Print ApplicationProperties::CFBundleVersion" "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")
    VERSION=$VERSION-$(/usr/libexec/PlistBuddy -c "Print ApplicationProperties:CFBundleShortVersionString" "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")"""

