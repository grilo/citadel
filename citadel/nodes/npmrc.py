#!/usr/bin/env python

import os

import citadel.nodes.node
import citadel.tools


class Npmrc(citadel.nodes.node.Base):
    """:synopsis: Generate an .npmrc file in the current directory.

    :requirements: None
    :platform: Any

    :param registry: The URL to the registry for the .npmrc file.
    :type registry: required

    :param email: The email to be used in the .npmrc file.
    :type email: required

    :param always_auth: Whether always-auth should be on/off.
    :type always_auth: optional

    :param strict_ssl: Whether strict-ssl should be on/off.
    :type strict_ssl: optional

    :param token: The authentication token (often used when publishing).
    :type token: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
          npmrc:
            registry: http://artifactory.company.com/api/npm/npm-repo
            email: owner@company.com
            always_auth: false
            strict_ssl: false
            token: d12a243482adasjnad

    .. warning::

        Avoid authentication tokens in plain text. CITADel does a best
        effort to remove them from the logs (anything containing the
        *password* string), but it's a very imperfect method.

    Generates an .npmrc file with the specified options. Any unknown options
    will be passed directly onto the .npmrc file.

    The NPM (Node Package Manager) is often used to run builds for JavaScript
    and/or run the installation of packages. It's up to the NPM command to
    know how to interpret these options, the module will simply generate the
    file.

    If the default directory (``$PWD``) is an awkward location, use the script
    directive to change the directory before invoking the npmrc module.

    Example:

    .. code-block:: yaml
        :linenos:

        build:
          script:
            - cd some/directory
          npmrc:
            registry: http://artifactory.company.com/api/npm/npm-repo
            email: owner@company.com
            always_auth: false
            strict_ssl: false
            token: d12a243482adasjnad
          npm: start run
    """

    def __init__(self, yml, path):
        super(Npmrc, self).__init__(yml, path)
        self.parser.add_default('always-auth', 'false')
        self.parser.add_default('strict-ssl', 'false')
        self.parser.add_default('token', 'undefined')
        errors, parsed, ignored = self.parser.validate()
        self.errors.extend(errors)
        self.output.append(
            self.generate_npmrc(
                parsed['always-auth'],
                parsed['strict-ssl'],
                parsed['token'],
            )
        )
        for k, v in ignored.items():
            self.output.append('echo "%s: %s" >> .npmrc' % (k, v))

    def generate_npmrc(self, always_auth, strict_ssl, token):
        return """
echo "Generating .npmrc file. If we're having authentication problems, ensure
the variable \$NPMAUTH is being passed through citadel."
echo "always-auth: %s" >> .npmrc
echo "strict-ssl: %s" >> .npmrc
echo "_token: %s" >> .npmrc
""" % (always_auth, strict_ssl, token)
