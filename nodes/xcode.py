#!/usr/bin/env python

import logging
import os

import nodes.root
import tools


class Xcode(nodes.root.Node):

    def __init__(self, yml, path):
        super(Xcode, self).__init__(yml, path)

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml.')
            return

        # Unsure if this is python3 compatible
        # Always display maven's version
        xcode_exec = tools.get_executable('xcodebuild')
        #if not xcode_exec:
        #    self.add_error('Unable to find xcodebuild in the path.')


        if 'build' in path:

            self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
            self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

            cmd = ['%s' % (xcode_exec)]
            lifecycle = 'clean archive'
            scheme = None
            archive_path = None

            if not 'scheme' in yml.keys():
                self.add_error('A scheme is necessary to know what to build.')
            else:
                scheme = yml['scheme']
                del yml['scheme']
            if not 'archivePath' in yml.keys():
                self.add_errors('An archive path needs to be specified (archivePath).')
            else:
                archive_path = os.path.join(os.getcwd(), yml['archivePath'])
                del yml['archivePath']

            cmd.append(' %s' % (lifecycle))
            cmd.append('-scheme "%s"' % (scheme))
            cmd.append('-archivePath "%s"' % (archive_path))

            if 'lifecycle' in yml.keys():
                lifecycle = yml['lifecycle']
                del yml['lifecycle']
            if 'workspace' in yml.keys():
                cmd.append('-workspace "%s"' % (yml['workspace']))
                del yml['workspace']
            if 'project' in yml.keys():
                cmd.append('-project "%s"' % (yml['project']))
                del yml['project']
            if 'configuration' in yml.keys():
                cmd.append('-configuration "%s"' % (yml['configuration']))
                del yml['configuration']

            if 'keychain' in yml.keys():
                if not 'keychain_password' in yml.keys():
                    self.add_error('A password is required when a keychain has been specified (keychain_password).')
                if not 'OTHER_CODE_SIGN_FLAGS' in yml.keys():
                    yml['OTHER_CODE_SIGN_FLAGS'] = ''
                yml['OTHER_CODE_SIGN_FLAGS'] += ' "--keychain \'%s\'' % (yml['keychain'])
                self.output.append('echo "Unlocking keychain for code signing."')
                self.output.append('/usr/bin/security list-keychains -s "%s"' % (yml['keychain']))
                self.output.append('/usr/bin/security default-keychain -d user -s "%s"' % (yml['keychain']))
                self.output.append('/usr/bin/security unlock keychain -p "%s" "%s"' % (yml['keychain_password'], yml['keychain']))
                self.output.append('/usr/bin/security set-keychain-settings -t 7200 "%s"' % (yml['keychain']))
            else:
                logging.warning('No "keychain" found, assuming it\'s already prepared.')

            if not 'CODE_SIGN_IDENTITY' in yml.keys():
                self.add_error('A code signing identity is required (CODE_SIGN_IDENTITY).')

            if not 'PROVISIONING_PROFILE_SPECIFIER':
                self.add_error('Missing team/provisioning_profile (PROVISIONING_PROFILE_SPECIFIER).')
            else:
                yml['DEVELOPMENT_TEAM'], yml['PROVISIONING_PROFILE'] = yml['PROVISIONING_PROFILE_SPECIFIER'].split('/')

            if not 'CONFIGURATION_BUILD_DIR' in yml.keys():
                yml['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), 'build')
            else:
                yml['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), yml['CONFIGURATION_BUILD_DIR'])

            for k, v in yml.items():
                cmd.append('%s="%s"' % (k, v))
            self.output.append('echo "Building..."')
            self.output.append(self.format_cmd(cmd))

            self.output.append('echo "Generating IPA file..."')
            export_cmd = ['%s' % (xcode_exec)]
            export_cmd.append('-exportArchive')
            export_cmd.append('-exportFormat ipa')
            export_cmd.append('-exportProvisioningProfile "%s"' % (yml['PROVISIONING_PROFILE']))
            export_cmd.append('-archivePath "%s"' % (archive_path))
            export_cmd.append('-exportPath "%s"' % (os.path.join(yml['CONFIGURATION_BUILD_DIR'], scheme + '.ipa')))
            self.output.append(self.format_cmd(export_cmd))
