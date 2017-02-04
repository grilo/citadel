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

        # Unsure if this is python3 compatible
        # Always display maven's version
        ansible_exec = citadel.tools.find_executable('ansible-playbook')
        parser = citadel.parser.Options(self.yml)

        if 'deploy' in path:
            parser.is_required('inventory')
            parser.is_required('playbook')

            errors, parsed, ignored = parser.validate()

            if len(errors):
                self.errors.extend(errors)
                return

            cmd = ['%s -v -i %s %s' % (ansible_exec, parsed['inventory'], parsed['playbook'])]

            for k, v in ignored.items():
                if k == 'inventory' or k == 'playbook':
                    continue
                cmd.append('-e %s=%s' % (k, v))
            self.output.append('echo "Deploying with ansible: %s"' % (parsed['playbook']))
            self.output.append(self.format_cmd(cmd))
