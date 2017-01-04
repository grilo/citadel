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

        if not 'build' in path:
            self.add_error('Xcode is only supported under a build directive.')

        self.defaults = {
            'lifecycle': 'clean archive',
            'OTHER_CODE_SIGN_FLAGS': '',
            'CONFIGURATION_BUILD_DIR': 'build',
            'CODE_SIGN_IDENTITY': '$CODE_SIGN_IDENTITY',
            'DEVELOPMENT_TEAM': '$TEAM_ID',
            'PROVISIONING_PROFILE_SPECIFIER': '$TEAM_ID/$UUID',
        }

        self.requirements = [
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
        ]

    def to_bash(self):

        output = []
        xcode_exec = citadel.tools.get_executable('xcodebuild')

        self.yml['CONFIGURATION_BUILD_DIR'] = os.path.join(os.getcwd(), self.yml['CONFIGURATION_BUILD_DIR'])
        if not 'exportPath' in self.yml.keys():
            self.yml['exportPath'] = os.path.join(self.yml['CONFIGURATION_BUILD_DIR'], self.yml['scheme'] + '.ipa')

        output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
        output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

        output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

        if 'keychain' in self.yml.keys():
            self.yml['OTHER_CODE_SIGN_FLAGS'] = self.yml['OTHER_CODE_SIGN_FLAGS']
            self.yml['OTHER_CODE_SIGN_FLAGS'] += ' --keychain \'%s\'' % (self.yml['keychain'])
            output.append(citadel.tools.unlock_keychain(self.yml['keychain'], self.yml['keychain_password']))
            output.append(citadel.tools.get_provisioning_profile(self.yml['app_id'], self.yml['keychain']))
        else:
            logging.warning('No "keychain" found, assuming it\'s already prepared.')

        export_cmd = ['%s' % (xcode_exec)]
        export_cmd.append('-exportArchive')
        export_cmd.append('-exportFormat ipa')
        export_cmd.append('-exportProvisioningProfile "$PP_NAME"')
        export_cmd.append('-archivePath "%s"' % (os.path.join(os.getcwd(), self.yml['archivePath'])))
        export_cmd.append('-exportPath "%s"' % (self.yml['exportPath']))

        cmd = ['%s' % (xcode_exec)]
        cmd.append(' %s' % (self.yml['lifecycle']))
        cmd.append('-scheme "%s"' % (self.yml['scheme']))
        cmd.append('-archivePath "%s"' % (self.yml['archivePath']))
        cmd.append('-configuration "%s"' % (self.yml['configuration']))
        if 'workspace' in self.yml.keys():
            cmd.append('-workspace "%s"' % (self.yml['workspace']))
        elif 'project' in self.yml.keys():
            cmd.append('-project "%s"' % (self.yml['project']))

        if 'target' in self.yml.keys():
            cmd.append('-target "%s"' % (self.yml['target']))
            del self.yml['target']

        to_delete = [
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
            'workspace',
            'project',
            'keychain',
            'keychain_password',
        ]

        exportPath = self.yml['exportPath']

        for d in to_delete:
            if d in self.yml.keys():
                del self.yml[d]

        for k, v in self.yml.items():
            cmd.append('%s="%s"' % (k, v))

        output.append('echo "Building..."')
        output.append(self.format_cmd(cmd))
        output.append('echo "Generating IPA file..."')
        output.append(self.format_cmd(export_cmd))
        output.append(citadel.tools.codesign_verify(exportPath))

        return output
