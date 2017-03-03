#!/usr/bin/env python

import citadel.nodes.node

class Wrap(citadel.nodes.node.Base):
    """:synopsis: Wrap command to generate valid YAML syntax.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
          preproduction:
            branch: master
            wrap:
              - maven:
                  lifecycle: clean install
              - maven:
                  lifecycle: verify

    This is mostly caused due to implementation details. The Yaml parser isn't
    able to properly detect and handle duplicate keys (and it shouldn't since
    it would otherwise break the specification and confuse users). This is
    often the situation when using the ``branch`` module.

    To work around that syntatic quirk, the ``wrap`` module should be used
    to allow multiple invokations of the same module within.

    .. warning::
        Incorrect example below!

    .. code-block:: bash
        :linenos:

        build:
          preproduction:
            branch: master
            - maven:
                lifecycle: clean install
            - maven:
                lifecycle: verify
    """

    def __init__(self, yml, path):
        super(Wrap, self).__init__(yml, path)
