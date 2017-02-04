#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.xcode


class XcodeBuild(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['scheme'] = 'helloworld'
        yml['archivePath'] = 'build/'
        yml['configuration'] = 'Debug'
        yml['workspace'] = 'blah'
        xcode = citadel.nodes.xcode.Xcode(yml, ['build'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(xcode.output)))
        self.assertEqual(len(xcode.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
