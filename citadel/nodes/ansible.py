#!/usr/bin/env python

import citadel.nodes.root
import citadel.tools


class Ansible(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Ansible, self).__init__(yml, path)
        self.playbook = yml

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml (expected dict).')
            return

        if not 'deploy' in path:
            self.add_error('Ansible is only supported within a deploy directive.')

        self.requirements = [
            'inventory',
            'playbook',
        ]

    def to_bash(self):
        output = []

        ansible_exec = citadel.tools.get_executable('ansible-playbook')
        cmd = ['%s -v -i %s %s' % (ansible_exec, self.yml['inventory'], self.yml['playbook'])]

        del self.yml['inventory']
        del self.yml['playbook']

        for k, v in self.yml.items():
            cmd.append('-e %s=%s' % (k, v))
        output.append(self.format_cmd(cmd))
        return output
