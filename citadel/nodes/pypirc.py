#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools


class Pypirc(citadel.nodes.node.Base):
    """:synopsis: Sets up a .pypirc configuration in the current dir.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        pypirc:
          pypi:
            repository: https://example.com/pypi
            username: <username>
            password: <password>
          other:
            repository: https://example.com/other
            username: <username>
            password: <password>

    .. warning::

        Avoid authentication tokens in plain text. CITADel does a best
        effort to remove them from the logs (anything containing the
        *password* string), but it's a very imperfect method.

    Generates a .pypirc in the current directory to allow custom package
    installation without super user privileges.

    The file is generating using the same format as describe in the package
    index section of the official distutils documentation. In addition to
    generating the .pypirc file itself it also re-sets the $HOME variable
    to the current directory to ensure all packages are installed in the
    local directory. Finally, adds the ``$HOME/.local/bin`` to $PATH so
    that any installed packages can be used as if they were globally
    installed.

    This directive depends on a working internet connection. If any proxy
    is required, remember to specific it either in the ``environment``
    directive or directly passing the http proxy's options using the
    ``-e "http_proxy=value"`` options through ``citadel-generate``.
    """

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
echo "Adding $(pwd)/.local/bin to PATH..."
export PATH=$PATH:$(pwd)/.local/bin
""" % (out)
