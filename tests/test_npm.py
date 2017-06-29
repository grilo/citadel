#!/usr/bin/env python

import unittest

import citadel.nodes.npm


class Npm(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['scheme'] = 'helloworld'
        yml['archivePath'] = 'build/'
        yml['configuration'] = 'Debug'
        yml['workspace'] = 'blah'
        npm = citadel.nodes.npm.Npm(yml, ['build'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(npm.output)))
        self.assertEqual(len(npm.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
