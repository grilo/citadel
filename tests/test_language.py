#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.language


class Language(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml = 'xcode8.1'
        language = citadel.nodes.language.Language(yml, ['build'])
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(language.output)))
        self.assertEqual(len(language.errors), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
