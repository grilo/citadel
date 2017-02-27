#!/usr/bin/env python

import glob

import citadel.nodes.node
import citadel.tools


class Npm(citadel.nodes.node.Base):
    """:synopsis: Runs the NPM executable.

    :requirements: None
    :platform: Any

    **Build**

    To run ``npm`` in a build directive, simply write the whole command line
    as you normally would. Example:

    .. code-block:: yaml
        :linenos:

        build:
          npm: compile run start --option=Value

    No options are currently supported.

	**Deploy**

	:param files: The files to publish.
	:type files: required

	:param registry: The registry to publish the packages to (defaults to npmjs.org).
	:type registry: optional

	:param scope: The scope to publish the packages under.
	:type scope: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        deploy:
          npm:
            files:
              - some_file.tgz
              - some_directory/
            registry: https://artifactory.company.com/api/npm/jspackages
            scope: somenamespace

    Publishes all the files present in the ``files`` directive with the
    provided parameters. It will simply loop over the files with all the
    given options. The ``deploy:npm`` directive translates into:

    If scope includes a "@" as prefix (*@scope*) it will be silently
    ignored.

    .. code-block:: bash
        :linenos:

        npm \\
            --registry https://artifactory.company.com/api/npm/jspackages \\
            --scope somenamespace \\
            publish \\
            some_file.tgz

        npm \\
            --registry https://artifactory.company.com/api/npm/jspackages \\
            --scope somenamespace \\
            publish \\
            some_directory

    """


    def __init__(self, yml, path):
        super(Npm, self).__init__(yml, path)

        npm_exec = citadel.tools.find_executable('npm')
        self.output.append('%s --version' % (npm_exec))

        if 'build' in path:
            self.output.append(npm_exec + ' ' + str(yml))

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
