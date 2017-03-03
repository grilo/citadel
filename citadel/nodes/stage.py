#!/usr/bin/env python

import citadel.nodes.node


class Stage(citadel.nodes.node.Base):
    """:synopsis: Placeholder and wrapper for the branch module.

    :requirements: None
    :platform: Any

    This module isn't meant to be used directly. It's just an implementation
    detail, a module to be loaded used whenever an unknown directive is
    found. In such case, the ``tree`` builder will look for a ``branch``
    directive within and, if found, will load this module to continue
    processing.
    """

    def __init__(self, yml, path):
        super(Stage, self).__init__(yml, path)
