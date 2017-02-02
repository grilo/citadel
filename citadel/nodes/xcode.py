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
                'app_id': None,
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

            if not validated['CONFIGURATION_BUILD_DIR'].startswith('/') and not validated['CONFIGURATION_BUILD_DIR'].startswith('$'):
                validated['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), validated['CONFIGURATION_BUILD_DIR'])
            if 'exportPath' in yml.keys():
                validated['exportPath'] = yml['exportPath']
            else:
                validated['exportPath'] = os.path.join(os.path.dirname(validated['archivePath']), validated['scheme'] + '.ipa')
                logging.debug('Setting exportPath to: %s', validated['exportPath'])

            self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
            self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')


            # ibtoold may timeout if CoreSimulator has weird stuff
            self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/CoreSimulator"/*')
            # Builds fail very often due to incorrect caching policies from Xcode (stored in DerivedData)
            self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

            cmd = ['%s' % (xcode_exec)]

            lifecycle = validated['lifecycle']
            scheme = validated['scheme']
            archive_path = validated['archivePath']
            if not validated['archivePath'].startswith('/') and not validated['archivePath'].startswith('$'):
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
                self.output.append(self.unlock_keychain(validated['keychain'], validated['keychain_password']))
                self.output.append(self.get_provisioning_profile(validated['app_id'], validated['keychain']))
            else:
                logging.warning('No "keychain" found, assuming it\'s already prepared.')

            cmd.append('CODE_SIGN_IDENTITY="$CODE_SIGN_IDENTITY"')
            cmd.append('DEVELOPMENT_TEAM="$TEAM_ID"')
            cmd.append('PROVISIONING_PROFILE_SPECIFIER="$TEAM_ID/$UUID"')


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
            self.output.append(self.codesign_verify(validated['exportPath']))

    def get_provisioning_profile(self, app_id, keychain):
        cmd = 'python /home/jenkins/CLI/utils/osx_pprofile.py -k %s' % (keychain)
        if app_id:
            cmd += ' -a %s' % (app_id)

        return '\n'.join([
            'cmd="%s"' % (cmd),
            'if [[ $ENVIRONMENT =~  PRO ]] ; then',
            '    cmd="$cmd --production"',
            'fi',
            'output=$($cmd)',
            'UUID=$(echo "$output" | head -1 | awk -F@ \'{print $1}\')',
            'PP_NAME=$(echo "$output" | head -1 | awk -F@ \'{print $2}\')',
            'CODE_SIGN_IDENTITY=$(echo "$output" | head -1 | awk -F@ \'{print $3}\')',
            'TEAM_ID=$(echo "$output" | head -1 | awk -F@ \'{print $4}\')',
        ])

    def unlock_keychain(self, keychain, password):
        return '\n'.join([
            'echo "Unlocking keychain for code signing."',
            '/usr/bin/security list-keychains -s "%s"' % (keychain),
            '/usr/bin/security default-keychain -d user -s "%s"' % (keychain),
            '/usr/bin/security unlock-keychain -p "%s" "%s"' % (password, keychain),
            '/usr/bin/security set-keychain-settings -t 7200 "%s"' % (keychain),
        ])

    def codesign_verify(self, ipafile):
        return '\n'.join([
            'unzip -oq -d "verifycodesign" "%s"' % (ipafile),
            'unpacked_app="$(ls verifycodesign/Payload/)"',
            'cd verifycodesign/Payload',
            'if ! codesign --verify --verbose=4 "$unpacked_app" --no-strict ; then',
            '    codesign -d -r -vvvvv "$unpacked_app"',
            '    echo "The application is not signed correctly."',
            '    echo "This may mean out of date certificate chains, probably hidden."',
            '    rm -fr "verifycodesign"',
            '    exit 1',
            'fi',
            'cd -',
            'rm -fr "verifycodesign"',
        ])
