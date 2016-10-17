#!/usr/bin/env python

import nodes.root


class Ansible(nodes.root.Node):

    def __init__(self, yml, path):
        super(Ansible, self).__init__(yml, path)
        self.playbook = yml

    def to_bash(self):
        output = []
        return output
