#!/usr/bin/env python

import logging
import re

import citadel.nodes.node
import citadel.tools


class Branch(citadel.nodes.node.Base):
    """:synopsis: Conditional execution based on regular expression by matching the source control's branch name.

    :requirements: git and/or accurev binary in the path
    :platform: Any

    :param name: A regular expression which will test the current branch's name
    :type name: required

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
            preproduction:
                name: (master|integration)
                maven:
                    lifecycle: clean install
            production:
                name: prod
                maven:
                    lifecycle: clean deploy

    .. note::

        This construct is special since any unknown module will be tested to see
        if it matches the criteriae to become a node of type ``branch``. This
        test is done by inspecting the children of the node. If any of the children
        contain a ``name`` key, a ``branch`` is instanced and normal operation
        will run as documented below. Otherwise, all nodes fraternal to ``name``
        will be ignored.

    The branch module is never used directly by itself. To enable conditional execution
    depending on environmental factors (in this case the underlying source control
    management), the branch module was created, enabling the same citadel file to be
    executed in multiple environments.

    Since each environment is very particular to every project/organization, the name
    of the possible environments is left to the user's choice and has no impact on the
    functionality itself (so long as it doesn't match an already existing module).

    **Example (good)**

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2

        deploy:
            homeinfotainment:
                name: infotainment
                ansible:
                    inventory: $ANSIBLE_HOME/home
                    playbook: $ANSIBLE_HOME/playbooks/deploy_infotainment.yml

    **Example (bad)**

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2

        deploy:
            maven:
                name: infotainment
                ansible:
                    inventory: $ANSIBLE_HOME/home
                    playbook: $ANSIBLE_HOME/playbooks/deploy_infotainment.yml


    As mentioned, the string which names the environment is completely arbitrary
    and does affect the logic underneath. Which means that:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2

        deploy:
            hello:
                name: somebranch
                script:
                    - echo "hello world"

    Is functionally equivalent to:

    .. code-block:: yaml
        :linenos:
        :emphasize-lines: 2

        deploy:
            world:
                name: somebranch
                script:
                    - echo "hello world"

    The ``name`` is a regular expression (as handled by python's ``re`` module)
    and can be used liberally:

    .. code-block:: yaml
        :linenos:

        deploy:
            some_environment:
                name: (!prod)

    This would match any branch which isn't named **prod**.

    The heuristic for matching branches depends on the driver being used.
    Currently both **git** and **AccuRev** are supported, and they are tested
    in that order. All the SCMs are testing and the last one succeeding takes
    precendence.

    In this case, if a directory is both an AccuRev workspace and a git repo,
    the AccuRev workspace would take precendence and be used for the actual
    evaluation of the branch's name.

    Git's branch name is detected by running:

    .. code-block:: bash

        git rev-parse --abbrev-ref HEAD

    AccuRev's branch name is detected by running:

    .. code-block:: bash

        accurev info

    """


    def __init__(self, yml, path):
        branch_name = self.get_branch_name()
        if re.search(yml, branch_name):
            logging.debug('Matched branch name for %s: %s', '/'.join(path), branch_name)
            super(Branch, self).__init__(yml, path)
        else:
            logging.debug('Branch name mismatch for %s. Expected [%s] instead got [%s])', '/'.join(path), yml, branch_name)
            self.skip = True

    def get_branch_name(self):
        branch_name = None

        # Git
        rc, out = citadel.tools.run_cmd('git rev-parse --abbrev-ref HEAD')
        if rc == 0:
            logging.debug('Git repo detected.')
            branch_name = out.strip()

        # AccuRev
        rc, out = citadel.tools.run_cmd('AccuRev info')
        if rc == 0:
            logging.debug('AccuRev repo detected.')
            for line in out.splitlines():
                if line.strip().startswith('Basis'):
                    branch_name = line.split(":")[-1].strip()
                    break

        if not branch_name:
            logging.warning('Unable to detect any branch name in the current directory.')
            return ''
        logging.info('Current branch: %s', branch_name)
        return branch_name
