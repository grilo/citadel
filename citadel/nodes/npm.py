#!/usr/bin/env python

import os

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
            registry = None
            scope = None
            file_list = []
            if 'registry' in yml.keys():
                registry = yml['registry']
            if 'scope' in yml.keys():
                scope = yml['scope']
            if isinstance(yml['files'], list):
                file_list.extend(yml['files'])
            else:
                file_list.append(yml['files'])
            for file_to_publish in file_list:
                dirname = os.path.dirname(file_to_publish)
                filename = os.path.basename(file_to_publish)
                self.output.append(self.publish_pkg(dirname, filename, registry, scope))

    def publish_pkg(self, directory, wildcard, registry=None, scope=None):
        """Run npm publish."""
        if not scope:
            scope = ''
        if registry:
            registry = "--registry " + registry
        else:
            registry = ''
        return """
filelist=$(find %s -maxdepth 1 -name "%s" | sort | grep -v "^%s$")
npmregistry="%s"
if [ $(echo "${filelist}" | wc -l) -eq 0 ] ; then
    echo "Unable to find any packages to publish!"
else
    cmd="npm $npmregistry"
    scope="%s"
    if [ ! -z "$scope" ] ; then
        cmd="$cmd --scope $scope"
    fi
    for pkg in $filelist ; do
        $cmd publish $pkg
    done
fi""" % (directory, wildcard, directory, registry, scope)
