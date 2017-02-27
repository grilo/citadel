#!/usr/bin/env python

import citadel.nodes.node


class Platform(citadel.nodes.node.Base):
    """:synopsis: Runs basic platform checks.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        platform: rhel6

    The initial concept was to provide docker based images or even pre-built
    Virtual Machines for the build environment. Currently this options is
    little more than a placeholder.

    If you are interested in using it, it supports the following checks:

    * rhel6
    * ubuntu

    If the system where the citadel-generated bash doesn't comply with those,
    it will abort instantly.
    """


    def __init__(self, yml, path):
        super(Platform, self).__init__(yml, path)
        if yml == "rhel6":
            self.output.append('if ! grep -q "Red Hat" /etc/redhat-release ; then')
            self.output.append('    echo "Requires a Red Hat system." && exit 1')
            self.output.append('fi')
        elif yml == "ubuntu":
            self.output.append('if ! grep -q "Ubuntu" /etc/issue ; then')
            self.output.append('    echo "Requires a Ubuntu system." && exit 1')
            self.output.append('fi')
