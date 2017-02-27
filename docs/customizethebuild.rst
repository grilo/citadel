Customize the Build
===================

By interpreting the file, CITADel will generate a bash script which will
execute with a set of specified parameters, or defaults if they aren't
mandatory. Nevertheless, it's possible to customer all the steps (which
ones and how many) in the ``citadel.yml`` file.

The yml descriptor will then show the job runner how to build your project
in each one of the lifecycle's steps. The ``citadel.yml`` file may be
minimalist or have as much execution logic as you desire. Examples of the
kind of parametrization possible:

* Programming language.
* Commands or scripts to be executed before or after each of the steps (such
  as cloning repositories, deleting files, etc.).
* How the generated binaries should be deployed.
* Which commands should be executed to test the project.
* Different behaviours depending on the environment.

Considerations
++++++++++++++

By default, the YAML specification does NOT guarantee order of execution. On
the other hand, CITADel does. This is the main reason why directives such as
``before_script`` or ``after_build`` aren't required - you may just write
the commands and the order will be respected.

As an example:

.. code-block:: yaml
    :linenos:

    deploy:
      script:
        - deploy_something.sh

    build:
      script:
        - build_something

CITADel will run the ``deploy`` step first and the ``build`` step after. This
means a non-sensical lifecycle may happen, but the alternatives don't really
fix that issue for you.

Build Lifecycle
+++++++++++++++

While there are no mandatory steps, CITADel will recognize 4 basic ones:

* ``build``: generates artifacts from the source code.
* ``publish``: upload the generated artifacts into some storage or file server.
* ``deploy``: deploy the artifacts, usually stored in the file server.
* ``test``: run tests (which require deployment).

If for whatever reason these aren't enough, it's **always** possible to
fallback to :class:`citadel.nodes.script`:

.. code-block:: yaml
    :linenos:

    build:
      script:
        - mvn clean install

