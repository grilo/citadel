#!/usr/bin/env python

import nodes.root


class Header(nodes.root.Node):

    def __init__(self, yml, path):
        super(Header, self).__init__(yml, path)
        self.output.append([
            '#!/usr/bin/env bash',
            '',
            'set -eu',
            'set -o pipefail',
        ]
