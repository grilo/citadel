#!/usr/bin/env python

import citadel.nodes.node


class Script(citadel.nodes.node.Base):
    """:synopsis: Wrapper for basic shell script lines.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
          script:
            - mvn clean install

    The lines within the module should all be under the form a list in yaml.
    These lines will get directly translated as shell script lines. The above
    example would become:

    .. code-block:: bash
        :linenos:

        mvn clean install

    This module is mainly a fallback for the user to be used whenever
    additional functionality is required and it hasn't be (or won't be)
    implemented.
    """

    def __init__(self, yml, path):
        super(Script, self).__init__(yml, path)
        self.output = yml
