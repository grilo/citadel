#!/usr/bin/env python

import unittest
import subprocess

import citadel.parser

class Citadel(unittest.TestCase):

    def setUp(self):
        yml = {
            'hello': 'world',
            'bye': 'world',
        }
        self.cit = citadel.parser.Options(yml)

    def test_default_parameters(self):
        self.cit.add_default('xpto', 'blah')
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(yml['xpto'], 'blah')

    def test_required_parameters_ok(self):
        self.cit.is_required('hello')
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_required_parameters_ko(self):
        self.cit.is_required('xpto')
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_at_least_one_ok(self):
        self.cit.at_least_one(['hello', 'bye'])
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_at_least_one_nok(self):
        self.cit.at_least_one(['xpto', 'world'])
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_at_most_one_ok(self):
        self.cit.at_most_one(['hello', 'xpto'])
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_at_most_one_nok(self):
        self.cit.at_most_one(['hello', 'bye'])
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_ignored_parameters(self):
        self.cit.at_most_one(['hello', 'xpto'])
        errors, yml, ignored = self.cit.validate()
        self.assertEqual(ignored, {'bye': 'world'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
