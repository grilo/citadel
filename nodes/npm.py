#!/usr/bin/env python

import nodes.root


class Npm(nodes.root.Node):

    def __init__(self, yml, path):
        super(Npm, self).__init__(yml, path)

        npm_exec = self.get_executable('npm')
        self.output.append('npm --version')

        if path[-2] == 'build':
            self.output.append(npm_exec + ' ' + yml)

        elif path[-2] == 'publish':
            if isinstance(yml, list):
                for pkg in yml: self.publish_pkg(pkg)
            else:
                self.publish_pkg(yml)

    def publish_pkg(self, pkg):
        npm_exec = self.get_executable('npm')
        self.output.append(npm_exec + ' publish ' + pkg)
