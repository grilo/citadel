#!/usr/bin/env python

import nodes.root


class Header(nodes.root.Node):

    def __init__(self, yml):
        super(Header, self).__init__(yml)

    def to_bash(self):
        return [
            '#!/usr/bin/env bash',
            '',
            'set -eu',
            'set -o pipefail',
        ]
