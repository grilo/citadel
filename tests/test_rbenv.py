#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.rbenv

class Rbenv(unittest.TestCase):

    def test_valid_parameters(self):
        yml = {}
        yml['ruby'] = 'hello world'
        yml['cocoapods'] = 'bye world'
        rbenv = citadel.nodes.rbenv.Rbenv(yml, '')

class RbenvRuby(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['ruby'] = '2.0.0'
        rbenv = citadel.nodes.rbenv.Rbenv(yml, '')
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(rbenv.output)))
        self.assertEqual(len(rbenv.errors), 0)

class RbenvCocoapods(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['cocoapods'] = '2.0.0'
        rbenv = citadel.nodes.rbenv.Rbenv(yml, '')
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(rbenv.output)))
        self.assertEqual(len(rbenv.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
