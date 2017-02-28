Getting Started
===============

Developers
++++++++++

Clone the contents of the citadel repository:

.. code-block:: bash
    :linenos:

    git clone https://github.com/grilo/citadel.git

Create a file called ``citadel.yml`` at the root of your project with the
following contents:

.. code-block:: yaml
    :linenos:


    platform: rhel6
    language: java1.7
    build:
      maven:
        lifecycle: clean install
    publish:
      maven:
        file: target/artifact.jar
        groupId: com.mycompany.myproject
        artifactId: service
        packaging: jar
    deploy:
      script:
        - wget http://artifactory/com/mycompany/myproject/service/LATEST/service-LATEST.jar
        - scp service-LATEST.jar user@remotehost:/aplicaciones/to_deploy/
        - /applications/scripts/deploy.sh artifact.jar

Run it:

.. code-block:: bash
    :linenos:

    python citadel/citadel-generate | bash

This example will build your java project by running the maven lifecycle. The
lifecycle will generate an artifact which will then get uploaded using the
``publish`` directive.

The ``deploy`` directive will then download the generated artifact, copy it
to a remote host and run a deployment script with the artifact as a parameter.

SysOps
++++++

Configure your job runner by following the steps below:

1. Ensure you have the latest version of CITADel:

.. code-block:: bash
    :linenos:

    git clone https://github.com/grilo/citadel.git

2. Run citadel against the project's root:

.. code-block:: bash
    :linenos:

    cd some_project
    python citadel/citadel-generate > build.sh
    bash build.sh

Optionally, you can run all ``citadel.yml`` found in the project's root
directory:

.. code-block:: bash
    :linenos:

    find . -type f -name "citadel.yml" -exec python citadel/citadel-generate -f {} | bash \;

CITADel may also depend on some environment variables, depending on which
modules are used. For instance, if you're using the module
:class:`citadel.nodes.ansible` it's strongly advised to set and pass the
``$ANSIBLE_HOME`` variable:

.. code-block:: bash
    :linenos:

    cd some_project
    python citadel/citadel-generate -e "ANSIBLE_HOME=/scm/git/ansible" > build.sh
    bash build.sh


A Primer on YAML
++++++++++++++++

There is extensive documentation available in
`Wikipedia <https://en.wikipedia.org/wiki/YAML>`_, but the important bit is
that YAML is very similar to JSON. The biggest difference is that it uses
whitespace/indentation to separate blocks instead of brackets ([]) or curly
braces ({}).

It supports two basic structures: key/value pairs and lists.

To defined a key/value:

.. code-block:: yaml
    :linenos:

    key: value
    another_key:
        sub_key_one: sub_value_one
        sub_key_two: sub_value_two

To define a list of values:

.. code-block:: yaml
    :linenos:

    key:
      - value_one
      - value_two
      - value_three

The following data structure in YAML:

.. code-block:: yaml
    :linenos:

    key: value
    another_key:
        sub_key_one: sub_value_one
        sub_key_two: sub_value_two
        sub_key_three:
          - value_one
          - value_two

Could be represented in JSON as:

.. code-block:: javascript
    :linenos:

    {
      key: "value",
      another_key: {
        sub_key_one: "sub_value_one",
        sub_key_two: "sub_value_two",
        sub_key_three: [
          "value_one",
          "value_two",
        ]
      }
    }

The biggest gotcha is the indentation. Below, a valid structure which would
result in an unexpected error:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3-5

    key: value
    another_key:
      some_value:
      - one_value
      - another_value

Though it may be unintuitive at first, it would be translated as:

.. code-block:: javascript
    :linenos:

    key: "value",
    another_key {
        some_value: none,
        [ one_value, another_value ],
    }

The correct form would be:

.. code-block:: yaml
    :linenos:
    :emphasize-lines: 3-5

    key: value
    another_key:
      some_value:
        - one_value
        - another_value
