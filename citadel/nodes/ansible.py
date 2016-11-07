#!/usr/bin/env python

import nodes.root
import tools


class Ansible(nodes.root.Node):

    def __init__(self, yml, path):
        super(Ansible, self).__init__(yml, path)
        self.playbook = yml

        if not isinstance(yml, dict):
            self.add_error('Parsing error, probably malformed yaml (expected dict).')
            return

        # Unsure if this is python3 compatible
        # Always display maven's version
        ansible_exec = tools.get_executable('ansible-playbook')

        if 'deploy' in path:
            if not 'inventory' in yml.keys():
                self.add_error('Deploying with ansible requires an "inventory" to be specified.')
                return
            if not 'playbook' in yml.keys():
                self.add_error('Deploying with ansible requires a "playbook" to be specified.')
                return

            cmd = ['%s -i %s %s' % (ansible_exec, yml['inventory'], yml['playbook'])]

            for k, v in yml.items():
                if k == 'inventory' or k == 'playbook':
                    continue
                cmd.append('-e %s=%s' % (k, v))
            self.output.append('echo "Deploying with ansible: %s"' % (yml['playbook']))
            self.output.append(self.format_cmd(cmd))
