#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.gradle


class Gradle(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['scheme'] = 'helloworld'
        yml['archivePath'] = 'build/'
        yml['configuration'] = 'Debug'
        yml['workspace'] = 'blah'
        gradle = citadel.nodes.gradle.Gradle(yml, ['build'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(gradle.output)))
        self.assertEqual(len(gradle.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
