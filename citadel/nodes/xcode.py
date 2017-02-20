#!/usr/bin/env python

import logging
import os

import citadel.nodes.node
import citadel.tools


class Xcode(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Xcode, self).__init__(yml, path)

        xcode_exec = citadel.tools.find_executable('xcodebuild')

        if not 'build' in path:
            return

        self.parser.add_default('app_id', None)
        self.parser.add_default('lifecycle', 'clean archive')
        self.parser.add_default('OTHER_CODE_SIGN_FLAGS', '')
#        self.parser.add_default('CONFIGURATION_BUILD_DIR', 'build')
        self.parser.add_default('CODE_SIGN_IDENTITY', '$CODE_SIGN_IDENTITY')
        self.parser.add_default('DEVELOPMENT_TEAM', '$TEAM_ID')
        self.parser.add_default('PROVISIONING_PROFILE_SPECIFIER', '$TEAM_ID/$UUID')

        self.parser.is_required('scheme')
        self.parser.is_required('archivePath')
        self.parser.is_required('configuration')
        self.parser.at_most_one(['workspace', 'project'])
        self.parser.if_one_then_all(['keychain', 'keychain_password'])

        errors, parsed, ignored = self.parser.validate()
        self.errors.extend(errors)
        if len(errors):
            return

        # Check for absolute paths
#        if not parsed['CONFIGURATION_BUILD_DIR'].startswith('/') and \
#            not parsed['CONFIGURATION_BUILD_DIR'].startswith('$'):
#            parsed['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), parsed['CONFIGURATION_BUILD_DIR'])

        # Set exportPath if it doesn't exist already
        if 'exportPath' in yml.keys():
            parsed['exportPath'] = yml['exportPath']
        else:
            parsed['exportPath'] = os.path.join(os.path.dirname(parsed['archivePath']), parsed['scheme'] + '.ipa')
            logging.debug('Setting exportPath to: %s', parsed['exportPath'])

        self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
        self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

        # ibtoold may timeout if CoreSimulator has weird stuff
        self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/CoreSimulator"/*')
        # Builds fail very often due to incorrect caching policies from Xcode (stored in DerivedData)
        self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

        cmd = ['%s' % (xcode_exec)]

        lifecycle = parsed['lifecycle']
        scheme = parsed['scheme']
        if not parsed['archivePath'].startswith('/') and not parsed['archivePath'].startswith('$'):
            parsed['archivePath'] = os.path.join(os.getcwd(), parsed['archivePath'])

        cmd.append(' %s' % (lifecycle))
        cmd.append('-scheme "%s"' % (parsed['scheme']))
        cmd.append('-archivePath "%s"' % (parsed['archivePath']))
        cmd.append('-configuration "%s"' % (parsed['configuration']))

        if 'workspace' in parsed.keys():
            cmd.append('-workspace "%s"' % (parsed['workspace']))
        elif 'project' in parsed.keys():
            cmd.append('-project "%s"' % (parsed['project']))

        if 'target' in ignored.keys():
            cmd.append('-target "%s"' % (ignored['target']))
            del ignored['target']

        if 'keychain' in parsed.keys():
            parsed['OTHER_CODE_SIGN_FLAGS'] += ' --keychain \'%s\'' % (parsed['keychain'])
            cmd.append('OTHER_CODE_SIGN_FLAGS="%s"' % (parsed['OTHER_CODE_SIGN_FLAGS']))
            self.output.append(self.unlock_keychain(parsed['keychain'], parsed['keychain_password']))
            self.output.append(self.get_provisioning_profile(parsed['app_id'], parsed['keychain']))
        else:
            logging.warning('No "keychain" found, assuming it\'s already prepared.')

        cmd.append('CODE_SIGN_IDENTITY="%s"' % (parsed['CODE_SIGN_IDENTITY']))
        cmd.append('DEVELOPMENT_TEAM="%s"' % (parsed['DEVELOPMENT_TEAM']))
        cmd.append('PROVISIONING_PROFILE_SPECIFIER="%s"' % (parsed['PROVISIONING_PROFILE_SPECIFIER']))

        for k, v in ignored.items():
            cmd.append('%s="%s"' % (k, v))
        self.output.append('echo "Building..."')
        self.output.append(citadel.tools.format_cmd(cmd))

        self.output.append('echo "Generating IPA file..."')
        export_cmd = ['%s' % (xcode_exec)]
        export_cmd.append('-exportArchive')
        export_cmd.append('-exportFormat ipa')
        export_cmd.append('-exportProvisioningProfile "$PP_NAME"')
        export_cmd.append('-archivePath "%s"' % (parsed['archivePath']))
        export_cmd.append('-exportPath "%s"' % (parsed['exportPath']))
        self.output.append(citadel.tools.format_cmd(export_cmd))
        self.output.append(self.codesign_verify(parsed['exportPath']))

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
