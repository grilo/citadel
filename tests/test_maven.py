#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.maven

class Maven(unittest.TestCase):

    def test_valid_parameters(self):
        yml = {}
        yml['ruby'] = 'hello world'
        yml['cocoapods'] = 'bye world'
        maven = citadel.nodes.maven.Maven(yml, '')

class MavenBuild(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['ruby'] = '2.0.0'
        maven = citadel.nodes.maven.Maven(yml, ['build'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(maven.output)))
        self.assertEqual(len(maven.errors), 0)

class MavenDeploy(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['file'] = 'hello.jar'
        yml['groupId'] = 'hello.jar'
        yml['artifactId'] = 'hello.jar'
        maven = citadel.nodes.maven.Maven(yml, ['publish'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(maven.output)))
        self.assertEqual(len(maven.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
