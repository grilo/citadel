#!/usr/bin/env python

import unittest
import subprocess

import citadel.nodes.ansible


class Ansible(unittest.TestCase):

    def test_output_string(self):
        yml = {}
        yml['inventory'] = 'blah'
        yml['playbook'] = 'blah'
        ansible = citadel.nodes.ansible.Ansible(yml, ['deploy'])
        self.assertEqual(len(ansible.errors), 0)
        self.assertTrue(citadel.tools.bash_syntax('\n'.join(ansible.output)))

if __name__ == '__main__':
    unittest.main(verbosity=2)
