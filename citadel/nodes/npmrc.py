#!/usr/bin/env python

import os

import citadel.nodes.node
import citadel.tools


class Npmrc(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Npmrc, self).__init__(yml, path)

        self.parser.add_default('always_auth', 'false')
        self.parser.add_default('strict_ssl', 'false')
        self.parser.add_default('token', 'undefined')

        self.parser.is_required('registry')
        self.parser.is_required('email')

        errors, parsed, ignored = self.parser.validate()
        self.errors.extend(errors)

        self.output.append(
            self.generate_npmrc(
                parsed['always_auth'],
                parsed['strict_ssl'],
                parsed['token'],
                parsed['registry'],
                parsed['email'],
            )
        )


    def generate_npmrc(self, always_auth, strict_ssl, token, registry, email):
        return """echo "Generating .npmrc file. If we're having authentication
problems, ensure the variable $NPMAUTH is being passed through citadel."
echo "email: %s" > .npmrc
echo "always-auth: %s" >> .npmrc
echo "strict-ssl: %s" >> .npmrc
echo "registry: %s" >> .npmrc
echo "_token: %s" >> .npmrc
""" % (always_auth, strict_ssl, token, registry, email)
