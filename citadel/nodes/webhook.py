#!/usr/bin/env python

import citadel.nodes.root
import citadel.tools


class Webhook(citadel.nodes.root.Node):

    def __init__(self, yml, path):
        super(Webhook, self).__init__(yml, path)

        # Unsure if this is python3 compatible
        # Always display maven's version
        curl_exec = citadel.tools.get_executable('curl')
        for url in yml:
            self.output.append(curl_exec + ' ' + url)