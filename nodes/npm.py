#!/usr/bin/env python

import glob

import nodes.root


class Npm(nodes.root.Node):

    def __init__(self, yml, path):
        super(Npm, self).__init__(yml, path)

        npm_exec = self.get_executable('npm')
        self.output.append('npm --version')

        if path[-2] == 'build':
            self.output.append(npm_exec + ' ' + yml)

        elif path[-2] == 'publish':
            registry = 'https://registry.npmjs.org'
            scope = None
            if 'registry' in yml.keys():
                registry = yml['registry']
            if 'scope' in yml.keys():
                scope = yml['scope']
            for pkg in yml['files']:
                # Make sure we support shell-like expansions
                # such as *.tgz
                globbed = glob.glob(pkg)
                if globbed:
                    for g in globbed:
                        self.publish_pkg(g, registry, scope)
                else:
                    self.publish_pkg(pkg, registry, scope)

    def publish_pkg(self, pkg, registry=None, scope=None):
        npm_exec = self.get_executable('npm')
        cmd = npm_exec
        if registry:
            cmd += ' --registry %s' % (registry)
        if scope:
            if not scope.startswith('@'):
                scope = '@' + scope
            cmd += ' --scope %s' % (scope)
        cmd += ' publish %s' % (pkg)
        self.output.append(cmd)
