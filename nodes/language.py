#!/usr/bin/env python

import nodes.root


class Language(nodes.root.Node):

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)
        if yml == 'java8':
            self.output.append('yum install openjdk1.8')
        elif yml == 'java7':
            self.output.append('yum install openjdk1.7')
        elif yml == 'java6':
            self.output.append('yum install openjdk1.6')
        else:
            raise Exception('Unsupported platform (%s).' % (yml))
