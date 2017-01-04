#!/usr/bin/env python

import zipfile
import glob
import os
import subprocess
import shlex
import distutils.spawn
import plistlib
import collections
import re
import plistlib
import logging

import citadel.yaml

def get_version(file, properties):
    version = None
    if file.endswith('.apk'):
        version = read_apk_version(file)
    elif file.endswith('.jar') or file.endswith('.war') or file.endswith('.ear'):
        return read_jar_version(file, properties['groupId'], properties['artifactId'])
    elif file.endswith('.ipa'):
        return read_ipa_version(file)
    else:
        logging.critical('Unknown file extension which prevents me from finding its version: %s', file)
    return version

def read_apk_version(file):
    cmd = 'AAPT_TOOL="$ANDROID_HOME/build-tools/$(ls -rt $ANDROID_HOME/build-tools | tail -1)/aapt"\n'
    cmd += 'VERSION=$($AAPT_TOOL d badging "%s" | grep versionName | awk -F\\\' \'{print $4"-"$6}\')' % (file)
    return cmd

def read_jar_version(file, group_id, artifact_id):
    return "VERSION=$(unzip -p '%s' '*%s*/*%s*/pom.properties' | grep version | awk -F= '{print $2}')" % (file, group_id, artifact_id)

def read_ipa_version(file):
    return """VERSION=$(/usr/libexec/PlistBuddy -c "Print ApplicationProperties::CFBundleVersion" "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")
VERSION=$VERSION-$(/usr/libexec/PlistBuddy -c "Print ApplicationProperties:CFBundleShortVersionString" "$(find ./* -type f -name Info.plist | grep "xcarchive/Info.plist")")"""

def get_alternatives(binary):
    try:
        rc, out = run_cmd('update-alternatives --list %s' % (binary))
    except OSError:
        rc, out = run_cmd('/usr/sbin/update-alternatives --display %s' % (binary))
        outlines = []
        for line in out.splitlines():
            if line.startswith('/'):
                outlines.append(re.sub(r' - .*', '', line))
        out = "\n".join(outlines)
    return out.splitlines()

def run_cmd(cmd):
    p = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    stdout, stderr = p.communicate()
    return p.returncode, stdout

def get_executable(executable):
    # Not sure if this is python3 compatible
    return distutils.spawn.find_executable(executable)

def get_branch_name(directory):
    branch_name = None
    old_dir = os.getcwd()
    os.chdir(directory)
    # Git
    rc, out = tools.run_cmd('git rev-parse --abbrev-ref HEAD')
    if rc == 0:
        branch_name = out.strip()
        logging.debug('Git repo detected. Branch: %s' % (branch_name))
    # AccuRev
    rc, out = tools.run_cmd('accurev info')
    if rc == 0:
        lines = [line for line in out.splitlines() if line.strip().startswith('Basis')]
        branch_name = lines[0].split(": ")[-1]
        logging.debug('AccuRev repo detected: %s' % (branch_name))

    os.chdir(old_dir)
    return branch_name

def unlock_keychain(keychain, password):
    return '\n'.join([
        'echo "Unlocking keychain for code signing."',
        '/usr/bin/security list-keychains -s "%s"' % (keychain),
        '/usr/bin/security default-keychain -d user -s "%s"' % (keychain),
        '/usr/bin/security unlock-keychain -p "%s" "%s"' % (password, keychain),
        '/usr/bin/security set-keychain-settings -t 7200 "%s"' % (keychain),
    ])

def codesign_verify(ipafile):
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

def ordered_load(stream, Loader=citadel.yaml.Loader, object_pairs_hook=collections.OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        citadel.yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return citadel.yaml.load(stream, OrderedLoader)

def get_provisioning_profile(app_id, keychain):
    cmd = 'osx_pprofile -k %s' % (keychain)
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

def filter_secrets(lines):
    filtered = []
    for line in lines:
        if re.search('.*password.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(password[\s:=]+)([\'"]*.*[\'"]*)[\s$].*', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        elif re.search('.*secret.*', line, flags=re.IGNORECASE):
            subbed = re.sub(r'(secret[\s:=]+)([\'"]*.*[\'"]*)[\s$]', r'\1(*** hidden ***) ', line)
            filtered.append(subbed)
        else:
            filtered.append(line)
    return filtered
