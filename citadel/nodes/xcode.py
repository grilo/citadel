#!/usr/bin/env python

import logging
import os

import citadel.nodes.root
import citadel.tools


class Xcode(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Xcode, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        xcode_exec = citadel.tools.get_executable('xcodebuild')
        if not xcode_exec:
            self.add_error('Unable to find Xcode executable.')

        if 'build' in path:

            self.set_defaults(yml, {
                'lifecycle': 'clean archive',
                'OTHER_CODE_SIGN_FLAGS': '',
                'CONFIGURATION_BUILD_DIR': 'build',
                'CODE_SIGN_IDENTITY': '$CODE_SIGN_IDENTITY',
                'DEVELOPMENT_TEAM': '$TEAM_ID',
                'PROVISIONING_PROFILE_SPECIFIER': '$TEAM_ID/$UUID',
            })

            # Extrac the required values
            validated = self.validate(yml, [
                'scheme',
                'app_id',
                'archivePath',
                'configuration',
                'lifecycle',
                'OTHER_CODE_SIGN_FLAGS',
                'CONFIGURATION_BUILD_DIR',
                'CODE_SIGN_IDENTITY',
                'DEVELOPMENT_TEAM',
                'PROVISIONING_PROFILE_SPECIFIER',
                ('workspace', 'project'),
                {'keychain': '', 'keychain_password': ''},
                ])

            for k in validated.keys():
                del yml[k]

            validated['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), validated['CONFIGURATION_BUILD_DIR'])
            if not 'exportPath' in validated.keys():
                validated['exportPath'] = os.path.join(validated['CONFIGURATION_BUILD_DIR'], validated['scheme'] + '.ipa')

            self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
            self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

            self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

            cmd = ['%s' % (xcode_exec)]

            lifecycle = validated['lifecycle']
            scheme = validated['scheme']
            archive_path = os.path.join(os.getcwd(), validated['archivePath'])

            cmd.append(' %s' % (lifecycle))
            cmd.append('-scheme "%s"' % (validated['scheme']))
            cmd.append('-archivePath "%s"' % (validated['archivePath']))
            cmd.append('-configuration "%s"' % (validated['configuration']))

            if 'workspace' in validated.keys():
                cmd.append('-workspace "%s"' % (validated['workspace']))
            elif 'project' in validated.keys():
                cmd.append('-project "%s"' % (validated['project']))

            if 'target' in yml.keys():
                cmd.append('-target "%s"' % (yml['target']))
                del yml['target']

            if 'keychain' in validated.keys():
                validated['OTHER_CODE_SIGN_FLAGS'] = validated['OTHER_CODE_SIGN_FLAGS']
                validated['OTHER_CODE_SIGN_FLAGS'] += ' --keychain \'%s\'' % (validated['keychain'])
                self.output.append(citadel.tools.unlock_keychain(validated['keychain'], validated['keychain_password']))
                self.output.append(citadel.tools.get_provisioning_profile(validated['app_id'], validated['keychain']))
            else:
                logging.warning('No "keychain" found, assuming it\'s already prepared.')

            for k, v in yml.items():
                cmd.append('%s="%s"' % (k, v))
            self.output.append('echo "Building..."')
            self.output.append(self.format_cmd(cmd))

            self.output.append('echo "Generating IPA file..."')
            export_cmd = ['%s' % (xcode_exec)]
            export_cmd.append('-exportArchive')
            export_cmd.append('-exportFormat ipa')
            export_cmd.append('-exportProvisioningProfile "$PP_NAME"')
            export_cmd.append('-archivePath "%s"' % (archive_path))
            export_cmd.append('-exportPath "%s"' % (validated['exportPath']))
            self.output.append(self.format_cmd(export_cmd))
            self.output.append(citadel.tools.codesign_verify(validated['exportPath']))
