#!/usr/bin/env python

import distutils.spawn

import nodes.root
import tools


class Webhook(nodes.root.Node):

    def __init__(self, yml, path):
        super(Webhook, self).__init__(yml, path)

        # Unsure if this is python3 compatible
        # Always display maven's version
        curl_exec = tools.get_executable('curl')
        for url in yml:
            self.output.append(curl_exec + ' ' + url)
