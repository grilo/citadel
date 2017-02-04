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

    def test_error_if_not_dict(self):
        cit = citadel.parser.Options(['hello', 'world'])
        errors, parsed, ignored = cit.validate()
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(parsed.keys()), 0)
        self.assertEqual(len(ignored.keys()), 0)
        error_message = False
        if 'malformed' in errors[0]:
            error_message = True
        self.assertTrue(error_message)

    def test_default_parameters(self):
        self.cit.add_default('xpto', 'blah')
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(parsed['xpto'], 'blah')

    def test_required_parameters_ok(self):
        self.cit.is_required('hello')
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_required_parameters_ko(self):
        self.cit.is_required('xpto')
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_at_least_one_ok(self):
        self.cit.at_least_one(['hello', 'bye'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_at_least_one_nok(self):
        self.cit.at_least_one(['xpto', 'world'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_at_most_one_ok(self):
        self.cit.at_most_one(['hello', 'xpto'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 0)

    def test_at_most_one_nok(self):
        self.cit.at_most_one(['hello', 'bye'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_if_one_then_all_ok(self):
        self.cit.at_most_one(['hello', 'bye'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_if_one_then_all_nok(self):
        self.cit.at_most_one(['hello', 'bye'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(len(errors), 1)

    def test_ignored_parameters(self):
        self.cit.at_most_one(['hello', 'xpto'])
        errors, parsed, ignored = self.cit.validate()
        self.assertEqual(ignored, {'bye': 'world'})


if __name__ == '__main__':
    unittest.main(verbosity=2)
