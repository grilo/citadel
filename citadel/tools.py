#!/usr/bin/env python    

import zipfile
import glob
import os
import subprocess
import shlex
import distutils.spawn
import plistlib


def get_version(file):
    version = None
    if file.endswith('.apk'):
        version = read_apk_version(file)
    elif file.endswith('.jar') or file.endswith('.war') or file.endswith('.ear'):
        return read_jar_version(file)
    elif file.endswith('.ipa'):
        return read_ipa_version(file)
    return version

def read_apk_version(file):
    cmd = 'AAPT_TOOL="$ANDROID_HOME/build-tools/$(ls -rt $ANDROID_HOME/build-tools | tail -1)/aapt"\n'
    cmd += 'VERSION=$($AAPT_TOOL d badging "%s" | grep versionName | awk -F\\\' \'{print $4"-"$6}\')' % (file)
    return cmd

def read_jar_version(file):
    return "unzip -p '%s' \*/pom.properties | grep version | awk -F= '{print $2}'" % (file)

def read_ipa_version(file):
    return "VERSION=$(/usr/libexec/PlistBuddy -c 'Print :CFBundleShortVersionString' /dev/stdin <<< $(unzip -p '%s' \*/Info.plist))" % (file)

def get_alternatives(binary):
    try:
        rc, out = run_cmd('update-alternatives --list %s' % (binary))
    except OSError:
        rc, out = run_cmd('/usr/sbin/update-alternatives --display %s' % (binary))
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
