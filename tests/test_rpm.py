#!/usr/bin/env python

import unittest
import subprocess
import os
import shutil

import citadel.nodes.rpm


class Rpm(unittest.TestCase):

    def setUp(self):
        yml = {}
        yml['files'] = ['hello.txt']
        yml['buildroot'] = '$(pwd)/builddir'
        yml['target'] = 'noarch'
        yml['Name'] = 'testrpm'
        yml['Version'] = '1'
        self.rpm = citadel.nodes.rpm.Rpm(yml, ['build'])

    def test_rpm_syntax(self):
        rpm = self.rpm
        self.assertEqual(len(rpm.errors), 0)
        if len(rpm.output) <= 0:
            self.assertTrue(False)
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(rpm.output)))

    def test_rpm_generation(self):
        rpm = self.rpm
        out = '\n'.join(rpm.output)

        contents = open('hello.txt', 'w')
        contents.write('something')
        contents.close()

        builder = open('tmp', 'w')
        builder.write(out)
        builder.close()
        subprocess.check_call(['bash', 'tmp'])
        os.unlink('tmp')
        os.unlink('hello.txt')
        subprocess.check_call(['rpm', '-qlp', os.path.join('builddir', 'RPMS', 'noarch', 'testrpm-1-1.noarch.rpm')])
        shutil.rmtree('builddir')

if __name__ == '__main__':
    unittest.main(verbosity=2)
