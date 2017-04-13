#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools


class Pypirc(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Pypirc, self).__init__(yml, path)

        self.output.append(self.generate_pypirc(yml))


    def generate_pypirc(self, pypirc):
        """Generate a .pypirc file."""

        out = """[distutils]
index-servers =
    """
        out += '\n    '.join(pypirc.keys())
        out += '\n'

        for index_server, properties in pypirc.items():
            out += '\n[%s]\n' % (index_server)
            for k, v in properties.items():
                out += "%s = %s\n" % (k, v)

        return """echo "%s" > .pypirc
echo "Re-setting HOME variable so the correct .pypirc file is read."
export HOME=$PWD
""" % (out)
