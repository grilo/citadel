#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools

class Ansible(citadel.nodes.node.Base):
    """:synopsis: Run ansible-playbook.

    :requirements: None
    :platform: Any

    :param inventory: The inventory file.
    :type inventory: required

    :param playbook: The playbook.
    :type playbook: required

    **Usage**

    .. code-block:: yaml
        :linenos:

        deploy:
          ansible:
            inventory: $ANSIBLE_HOME/inventory/development
            playbook: $ANSIBLE_HOME/playbooks/some_playbook.yml

    The paths for both the inventory and playbook files may be hardcoded, but
    but the environment is expected to provide an ANSIBLE_HOME variable to be
    referenced from within the yaml.

    Additional parameters may be specified and will be globbed up into the **-e** option
    of ansible-playbook's CLI.

    .. code-block:: yaml
        :linenos:

        deploy:
          ansible:
            inventory: $ANSIBLE_HOME/development
            playbook: $ANSIBLE_HOME/playbooks/some_playbook.yml
            parameter: value
            another_parameter: value


    Would be transformed into:

    .. code-block:: bash
        :linenos:

        # Assumes ANSIBLE_HOME=/path/to
        ansible-playbook -i /path/to/inventory/development \\
            -e "parameter=value" \\
            -e "another_parameter=value" \\
            /path/to/playbooks/some_playbook.yml
    """

    def __init__(self, yml, path):
        super(Ansible, self).__init__(yml, path)
        self.playbook = yml

        ansible_exec = citadel.tools.find_executable('ansible-playbook')

        self.parser.is_required('inventory')
        self.parser.is_required('playbook')

        errors, parsed, ignored = self.parser.validate()

        if len(errors):
            self.errors.extend(errors)
            return

        cmd = ['%s -v -i %s %s' % (ansible_exec, parsed['inventory'], parsed['playbook'])]

        for key, value in ignored.items():
            cmd.append('-e %s=%s' % (key, value))
        self.output.append('echo "Deploying with ansible: %s"' % (parsed['playbook']))
        self.output.append(citadel.tools.format_cmd(cmd))
