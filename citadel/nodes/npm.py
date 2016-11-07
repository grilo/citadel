#!/usr/bin/env python

import glob

import citadel.nodes.root
import citadel.tools


class Npm(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Npm, self).__init__(yml, path)

        npm_exec = citadel.tools.get_executable('npm')
        self.output.append('npm --version')

        if 'build' in path:
            self.output.append(npm_exec + ' ' + yml)

        elif 'publish' in path:
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
        npm_exec = citadel.tools.get_executable('npm')
        cmd = npm_exec
        if registry:
            cmd += ' --registry %s' % (registry)
        if scope:
            if not scope.startswith('@'):
                scope = '@' + scope
            cmd += ' --scope %s' % (scope)
        cmd += ' publish %s' % (pkg)
        self.output.append(cmd)
