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

        # Unsure if this is python3 compatible
        xcode_exec = citadel.tools.get_executable('xcodebuild')


        if 'build' in path:

            self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
            self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

            self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

            cmd = ['%s' % (xcode_exec)]
            lifecycle = 'clean archive'
            scheme = None
            archive_path = None
            export_path = None
            configuration = None
            target = None
            keychain = None
            app_id = None

            if not 'app_id' in yml.keys():
                logging.critical('An app_id is missing. This will default to wildcard profile - are you sure?')
            else:
                app_id = yml['app_id']
                del yml['app_id']

            if not 'scheme' in yml.keys() and not 'project' in yml.keys():
                self.add_error('A scheme or project are necessary to know what to build.')

            if not 'archivePath' in yml.keys():
                self.add_errors('An archive path needs to be specified (archivePath).')
            else:
                archive_path = os.path.join(os.getcwd(), yml['archivePath'])
                del yml['archivePath']
            if not 'configuration' in yml.keys():
                self.add_error('A configuration is required (Release/Debug).')
            else:
                configuration = yml['configuration']
                del yml['configuration']

            cmd.append(' %s' % (lifecycle))
            cmd.append('-archivePath "%s"' % (archive_path))
            cmd.append('-configuration "%s"' % (configuration))

            if 'scheme' in yml.keys():
                scheme = yml['scheme']
                cmd.append('-scheme "%s"' % (yml['scheme']))
                del yml['scheme']
            if 'lifecycle' in yml.keys():
                lifecycle = yml['lifecycle']
                del yml['lifecycle']
            if 'workspace' in yml.keys():
                cmd.append('-workspace "%s"' % (yml['workspace']))
                del yml['workspace']
            if 'project' in yml.keys():
                cmd.append('-project "%s"' % (yml['project']))
                del yml['project']
            if 'target' in yml.keys():
                cmd.append('-target "%s"' % (yml['target']))
                del yml['target']

            if 'keychain' in yml.keys():
                if not 'keychain_password' in yml.keys():
                    self.add_error('A password is required when a keychain has been specified (keychain_password).')
                if not 'OTHER_CODE_SIGN_FLAGS' in yml.keys():
                    yml['OTHER_CODE_SIGN_FLAGS'] = ''
                keychain = yml['keychain']
                yml['OTHER_CODE_SIGN_FLAGS'] += ' --keychain \'%s\'' % (keychain)
                self.output.append(citadel.tools.unlock_keychain(keychain, yml['keychain_password']))
                del yml['keychain']
                del yml['keychain_password']
            else:
                logging.warning('No "keychain" found, assuming it\'s already prepared.')

            if 'entitlement' in yml.keys():
              yml['CODE_SIGN_ENTITLEMENTS'] =  (yml['entitlement'])
              del yml['entitlement']

            if not 'CODE_SIGN_IDENTITY' in yml.keys() \
                and not 'PROVISIONING_PROFILE_SPECIFIER' in yml.keys() \
                and keychain:
                self.output.append(citadel.tools.get_provisioning_profile(app_id, keychain))
                yml['CODE_SIGN_IDENTITY'] = '$CODE_SIGN_IDENTITY'
                yml['PROVISIONING_PROFILE_SPECIFIER'] = '$TEAM_ID/$UUID'

            if not 'PROVISIONING_PROFILE_SPECIFIER':
                self.add_error('Missing team/provisioning_profile (PROVISIONING_PROFILE_SPECIFIER).')
            else:
                yml['DEVELOPMENT_TEAM'] = '$TEAM_ID'

            if not 'CONFIGURATION_BUILD_DIR' in yml.keys():
                yml['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), 'build')
            else:
                yml['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), yml['CONFIGURATION_BUILD_DIR'])

            if not 'exportPath' in yml.keys() and scheme:
                export_path = os.path.join(yml['CONFIGURATION_BUILD_DIR'], scheme + '.ipa')

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
            export_cmd.append('-exportPath "%s"' % (export_path))
            self.output.append(self.format_cmd(export_cmd))
            if not export_path:
                logging.critical('Unable to verify codesign: export_path variable is empty. Contact soporteqa@ingdirect.es')
            else:
                self.output.append(citadel.tools.codesign_verify(export_path))
