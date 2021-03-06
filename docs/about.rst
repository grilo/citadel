About
=====

CITADel (Continuous Integration Testing And DELivery) is heavily inspired by
tools such as `<https://travis-ci.org>`_, `<https://circleci.com>`_ and the
likes. The goal is to provide autonomy and allow the developer to decouple
his/her project from the standard lifecycle tools such as Jenkins.

The citadel.yml file (by default, it can be anything else) describes your
project's lifecycle. It's not an executor/runner by itself, it simply
translates whatever there is in the yml file into standard bash which can then
be executed at your discretion.

By describing the build/deployment using a yaml file (the complexity will vary
depending on the requirements), you can now run your application's lifecycle
in any environment (currently it must support bash). This means that any
Jenkins job you configure simply needs to invoke CITADel and the rest will be
taken care of, effectively transforming your own CI solution into something
similar to other offerings from the cloud.

Although third party offerings are nothing short of fantastic, in the
corporate environment they're often not a choice due to internal budget
restrictions or security concerns. The "jenkinsfile" concept is sound,
but it's attached to a specific tool (Jenkins) and lacks any meaningful
documentation to actually be of value.

It's a complement to the tools usually used to build projects (such as maven,
gradle, npm). Those tools usually excel at generating artifacts (condensed
in the build and publish phase of CITADel), but they aren't very friendly
when it comes to deploying and testing the actual product.

Design Goals
++++++++++++

#. Modules are standalone/self-contained and are easy to create.
#. The modules generate a script which may be executed on any host
   (of the same family).
#. No code should be executed on the system where CITADel is being executed,
   unless strictly required (such as checking for branch names, another
   notable exception is when dealing with provisioning profiles for Xcode
   builds).
#. Idempotence: the resulting shell script should be able to be copy/pasted
   into another system and have the exact same behaviour.
#. When in doubt, make it easier to the user at the expense of the module
   creator.

Architecture
++++++++++++

CITADel will load the yaml file by using its own internal parser (PyYAML,
with very topical changes).

With the existing structure (a python dictionary), it will then traverse it
recursively and try to match any keys of the dictionary with existing modules.
The module in charge of parsing the dictionary may be found in
citadel.tree.Builder.

If the module is found, it will be loaded and the value belonging to that key
will be passed on to the module. It will recursively continue to look for
additional modules. This means that the following structure may result in
the incorrect generation of a tree:

.. code-block:: yaml
    :linenos:

    build:
      maven:
        lifecycle: clean install
        maven: hello

Since the maven module will be loaded twice, the second one will result in
an error since "hello" is invalid input to the maven module. Most modules
expect a map, though there are exceptions (such as
:class:`citadel.nodes.script`).

The module :class:`citadel.tree.builder` will create a standard tree, each
node able to containg N children.

When the tree is finished being built, if any errors are found it will abort
instantly. If there are no errors, the module :class:`citadel.tree.walker`
will parse each node and extract the generated values (currently Bash script)
which will then be output to STDOUT.

Syntax
++++++

The structure of a ``citadel.yml`` file is as follows:

.. code-block:: yaml
    :linenos:

    platform: targeted_platform
    language: used_language

    environment:
      name1: value1
      name2: value2

    build:
      targeted_branch1:
        branch: branch1_name
        script:
          - comand1
          - comand2
        used_builder:
          arg1: value1
          arg2: value2
      targeted_branch2:
        branch: branch2_name
        used_builder:
          arg1: value1
          arg2: value2

    publish:
      script:
        - comand1
        - comand2
      targeted_branch1:
        branch: branch1_name
        used_publisher:
          arg1: value1
          arg2: value2
      targeted_branch2:
        branch: branch2_name
        used_publisher:
          arg1: value1
          arg2: value2

    deploy:
      targeted_branch1:
        branch: branch1_name
        used_deployer:
          arg1: value1
          arg2: value2
      targeted_branch2:
        branch: branch2_name
        used_deployer:
          arg1: value1
          arg2: value2
