#!/usr/bin/env python

import nodes.root


class Platform(nodes.root.Node):

    def __init__(self, yml):
        super(Platform, self).__init__(yml)

    def to_bash(self):
        output = []
        if self.yml['platform']['os'] == 'linux':
            if self.yml['platform']['language'] == 'java8':
                output.append('yum install openjdk1.8')
            if self.yml['platform']['language'] == 'java7':
                output.append('yum install openjdk1.7')
            if self.yml['platform']['language'] == 'java6':
                output.append('yum install openjdk1.6')
        else:
            raise Exception("Unsupported platform.")
        return output
