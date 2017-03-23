#!/usr/bin/env python

import logging
import os

import citadel.nodes.node
import citadel.tools


class Xcode(citadel.nodes.node.Base):
    """:synopsis: Runs Xcode on the current directory.

    :requirements: Xcode executable, osx_pprofile
    :platform: OSX

    :param scheme: The scheme to be built.
    :type scheme: required

    :param archivePath: The path where the application's binary will reside.
    :type archivePath: required

    :param workspace: The workspace to build (mutually exclusive with project).
    :type workspace: required

    :param project: The project to build (mutually exclusive with project).
    :type project: required

    :param keychain: The path to the keychain to use when signing the binary.
    :type keychain: optional

    :param keychain_password: The password to unlock the keychain.
    :type keychain_password: required if keychain is specified

    :param app_id: The application's identifier (com.company.app)
    :type app_id: optional

    :param lifecycle: The lifecycle use when building (default: clean archive)
    :type lifecycle: optional

    :param OTHER_CODE_SIGN_FLAGS: Additional options to pass to xcodebuild
    :type OTHER_CODE_SIGN_FLAGS: optional

    :param CODE_SIGN_IDENTITY: The code signing identity to use when signing
    :type CODE_SIGN_IDENTITY: optional

    :param DEVELOPMENT_TEAM: The development team to use when signing.
    :type DEVELOPMENT_TEAM: optional

    :param PROVISIONING_PROFILE_SPECIFIER: The provisioning profile specifier.
    :type PROVISIONING_PROFILE_SPECIFIER: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        rbenv:
            ruby: 2.3.0
            cocoapods: 1.1.0

        build:
          script:
            - rm -fr build
            - chmod -R +w *
          xcode:
            app_id: com.company.app
            lifecycle: clean archive
            scheme: SomeName
            workspace: SomeName.xcworkspace
            archivePath: build/SomeName.xcarchive
            configuration: Debug
            keychain: /Users/jenkins/Library/Keychains/default.keychain
            keychain_password: $KEYCHAIN_PASSWORD
            ENABLE_BITCODE: NO
            IPHONEOS_DEPLOYMENT_TARGET: 6.0

    .. warning::

        This module will delete the ~/Library/Developer/CoreSimulator and the
        ~/Library/Developer/Xcode/DerivedData directories regardless. Make
        sure there are no builds being executed concurrently.

        The keychain password should not be written directly into the citadel.yml
        file for security reasons. Pass the value as an environment variable:
        ``citadel-generate -e "KEYCHAIN_PASSWORD=securestring"``.

    The Xcode module is extremely complex due to the requirements it has when
    invoking it from the command line. From the GUI everything seems a bit
    magical, but what's actually happening underneath is far from it.

    Most of the above options should be known to you if you're developing
    applications with Xcode and have a reasonable degree of knowledge about
    the options it provides. As such, those details will not be discussed
    here.

    If no app_id is specified, the module will attempt to find a
    wildcard provisioning profile and corresponding certificate to sign the
    application.

    Given the keychain and app_id, it will use an utility to look for the
    best matching provisioning profile/certificate to be used. This is a
    heuristic and may not match the best. If bugs are found, please contact
    the author.

    The provisioning profile search is done using
    `<https://github.com/grilo/ppbuddy>`_.

    Any unknown options will be treated as Xcode options. The following:

    .. code-block:: yaml
        :linenos:

          xcode:
            [...]
            ENABLE_BITCODE: NO
            IPHONEOS_DEPLOYMENT_TARGET: 6.0

    Would be passed down as:

    .. code-block:: bash
        :linenos:

        xcodebuild clean archive \\
            [...] \\
            ENABLE_BITCODE=NO \\
            IPHONEOS_DEPLOYMENT_TARGET=6.0
    """

    def __init__(self, yml, path):
        super(Xcode, self).__init__(yml, path)

        xcode_exec = citadel.tools.find_executable('xcodebuild')

        if not 'build' in path:
            return

        self.parser.add_default('app_id', None)
        self.parser.add_default('lifecycle', 'clean archive')
        self.parser.add_default('OTHER_CODE_SIGN_FLAGS', '')
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

        # Set exportPath if it doesn't exist already
        if 'exportPath' in yml.keys():
            parsed['exportPath'] = yml['exportPath']
        else:
            parsed['exportPath'] = os.path.join(os.path.dirname(parsed['archivePath']),
                                                parsed['scheme'] + '.ipa')
            logging.debug('Setting exportPath to: %s', parsed['exportPath'])

        self.output.append('echo "Xcodebuild version: $(xcodebuild -version)"')
        self.output.append('echo "Bundle version: $(/usr/bin/agvtool mvers -terse1)"')

        # ibtoold may timeout if CoreSimulator has weird stuff
        self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/CoreSimulator"/*')
        # Builds fail very often due to incorrect caching policies from Xcode
        # (stored in DerivedData)
        self.output.append('rm -fr "/Users/$(whoami)/Library/Developer/Xcode/DerivedData"/*')

        cmd = ['%s' % (xcode_exec)]

        lifecycle = parsed['lifecycle']
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
            cmd.append('OTHER_CODE_SIGN_FLAGS="%s"' %
                       (parsed['OTHER_CODE_SIGN_FLAGS']))
            self.output.append(self.unlock_keychain(
                parsed['keychain'], parsed['keychain_password']))
            self.output.append(self.get_provisioning_profile(parsed['app_id'], parsed['keychain']))
        else:
            logging.warning('No "keychain" found, assuming it\'s already prepared.')

        cmd.append('CODE_SIGN_IDENTITY="%s"' % (parsed['CODE_SIGN_IDENTITY']))
        cmd.append('DEVELOPMENT_TEAM="%s"' % (parsed['DEVELOPMENT_TEAM']))
        cmd.append('PROVISIONING_PROFILE_SPECIFIER="%s"' %
                   (parsed['PROVISIONING_PROFILE_SPECIFIER']))

        for key, value in ignored.items():
            cmd.append('%s="%s"' % (key, value))
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
        """Download ppbuddy.py and run it.

        Obtains the best provisioning profile/certificate combo."""
        cmd = 'python ppbuddy/ppbuddy.py -k %s' % (keychain)
        if app_id:
            cmd += ' -a %s' % (app_id)
        return """
if [ -d ppbuddy ] ; then
    rm -fr ppbuddy
fi
git clone https://github.com/grilo/ppbuddy.git
cmd="%s"
if [[ $ENVIRONMENT =~  PRO ]] ; then
    cmd="$cmd --production"
fi
output=$($cmd)
UUID=$(echo "$output" | head -1 | awk -F@ '{print $1}')
PP_NAME=$(echo "$output" | head -1 | awk -F@ '{print $2}')
CODE_SIGN_IDENTITY=$(echo "$output" | head -1 | awk -F@ '{print $3}')
TEAM_ID=$(echo "$output" | head -1 | awk -F@ '{print $4}')""" % (cmd)

    def unlock_keychain(self, keychain, password):
        """Unlockes the keychain, required to digitally sign apps."""
        return """echo "Unlocking keychain for code signing."
keychain="%s"
/usr/bin/security list-keychains -s "$keychain"
/usr/bin/security default-keychain -d user -s "$keychain"
/usr/bin/security unlock-keychain -p "%s" "$keychain"
/usr/bin/security set-keychain-settings -t 7200 "$keychain" """ % (keychain, password)

    def codesign_verify(self, ipafile):
        """Ensure the code signing was done properly."""
        return """unzip -oq -d "verifycodesign" "%s"
unpacked_app="$(ls verifycodesign/Payload/)"
cd verifycodesign/Payload
if ! codesign --verify --verbose=4 "$unpacked_app" --no-strict ; then
    codesign -d -r -vvvvv "$unpacked_app"
    echo "The application is not signed correctly."
    echo "This may mean out of date certificate chains, probably hidden."
    rm -fr "verifycodesign"
    exit 1
fi
cd -
rm -fr "verifycodesign" """ % (ipafile)
