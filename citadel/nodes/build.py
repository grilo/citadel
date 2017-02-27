#!/usr/bin/env python

import citadel.nodes.node


class Build(citadel.nodes.node.Base):
    """:synopsis: Placeholder for the build stage.

    :requirements: None
    :platform: Any

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
		  maven:
            lifecycle: clean install

    This module is simply part of the convention to run citadel by stages.
    Other supported stages are: publish, deploy and test. These are used
    to control their execution at specific moments since, at some points
    of your lifecycle you may wish to simply run the build and publish
    stages, or just the deploy, without having to run the whole thing.

    Stages get used when invoking the CLI of citadel itself:

    .. code-block:: bash
        :linenos:

        citadel-generate -i build,publish,test

    Would ignore the build and publish phases, and compute whatever
    there is left in the citadel.yml file (likely the deploy).

    If you just want to run the build, you could:

    .. code-block:: bash
        :linenos:

        citadel-generate -i publish,deploy,test
    """


    def __init__(self, yml, path):
        super(Build, self).__init__(yml, path)
        self.output.append('\necho "### Build ###"')
