Getting Started
===============

Create a new file called ``citadel.yml`` to the root of your project with the
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

This example will build your java project by running the maven lifecycle. The
lifecycle will generate an artifact which will then get uploaded using the
``publish`` directive.

The ``deploy`` directive will then download the generated artifact, copy it
to a remote host and run a deployment script with the artifact as a parameter.
