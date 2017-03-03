#!/usr/bin/env python

import citadel.nodes.node


class Environment(citadel.nodes.node.Base):
    """:synopsis: Define environment variables.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        environment:
          key: value
          PATH: /usr/bin

    Converts all the keys and values into equivalent bash statements that
    assign and export the variables, thus making them world-readable for
    the process and all its children (which is standard bash behaviour).

    The above example would get translated into:

    .. code-block:: bash
        :linenos:

        export key=value
        export PATH=/usr/bin

    """

    def __init__(self, yml, path):
        super(Environment, self).__init__(yml, path)
        self.output.append('\necho "### Environment Variables ###"')
        if isinstance(yml, list):
            for line in yml:
                self.output.append('export %s' % (line))
        elif isinstance(yml, dict):
            for key, value in yml.items():
                self.output.append('export %s=%s' % (key, value))
