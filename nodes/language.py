#!/usr/bin/env python

import subprocess
import shlex

import nodes.root


class Language(nodes.root.Node):

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)
        alternatives = subprocess.check_output(shlex.split('update-alternatives --list javac')).split("\n")
        javac = None
        for alt in alternatives:
            if 'javac' in alt and 'java-8' in alt:
                javac = alt
        if not javac:
            raise Exception('Unsupported language (%s).' % (yml))

        java_home = javac.split("/bin/javac")[0]
        self.output.append('export JAVA_HOME=%s' % (java_home))
