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


Examples
++++++++

These aren't necessarily the best examples in the world, they're simply to
showcase the possibilities of standard configurations required for relatively
complex lifecycles.

Android APK
-----------

.. code-block:: yaml
    :linenos:

	platform: android
	language: java1.8

	build:
	  script:
		- git checkout $BRANCH
		- bash configure_workspace.sh from_bundles
	  gradle:
		lifecycle: clean assemble

	publish:
	  development:
		branch: DEV
		maven:
		  file: Native-Android/build/outputs/apk/Native-Android-debug-unaligned.apk
		  artifactId: NATIVEFRAME
		  groupId: com.company.android
		  packaging: apk
		  url: http://jenkins.company.com:8080/artifactory/repo-snapshots
		  snapshot: True
		  generatePom: True
		  repositoryId: repo-snapshots
		  opts: -q -B -U -s /home/jenkins/.m2/settings.xml
	  preproduction:
		branch: PRE
		maven:
		  file: Native-Android/build/outputs/apk/Native-Android-debug-unaligned.apk
		  artifactId: NATIVEFRAME
		  groupId: com.company.android
		  packaging: apk
		  url: http://jenkins.company.com:8080/artifactory/repo-snapshots
		  snapshot: True
		  generatePom: True
		  repositoryId: repo-snapshots
		  opts: -q -B -U -s /home/jenkins/.m2/settings.xml
	deploy:
	  development:
		branch: DEV
		ansible:
		  inventory: $ANSIBLE_HOME/environments/development
		  playbook: $ANSIBLE_HOME/playbooks/deploy_nativeapps.yml
		  platform: ANDROID
		  packaging: apk
		  artifact_group: com.company.android
		  artifact_id: nativeframe
		  version: latest
		script:
		  - perl /home/jenkins/CLI/utils/nativeapps/generate_index.pl -c "/home/jenkins/.ssh/jenkins.rsa"

iOS IPA
-------

.. code-block:: yaml
    :linenos:

	platform: ios
	language: xcode-beta

	build:
	  script:
		- pod setup
		- pod install
		- sed -i .bak s/'com.provider.iosapp'/'com.company.iosapp'/"Application release-Info.plist"
		- sed -i .bak s/'com.provider.iosapp'/'com.company.iosapp'/"Application-Info.plist"
		- sed -i .bak s/'com.provider.iosapp'/'com.company.iosapp'/"Application.xcodeproj/project.pbxproj"
	  xcode:
		app_id: com.company.iosapp
		lifecycle: clean archive
		workspace: Application.xcworkspace
		scheme: AppScheme
		archivePath: build/Application.xcarchive
		configuration: Debug
		keychain: /Users/jenkins/Library/Keychains/mobileapps.keychain
		keychain_password: $KEYCHAIN_PASSWORD
		entitlement: Application/Application.entitlements
		ENABLE_BITCODE: No
		IPHONEOS_DEPLOYMENT_TARGET: 6.0

	publish:
	  development:
		branch: DEV
		maven:
		  file: build/Application.ipa
		  artifactId: iosapp
		  groupId: com.company
		  packaging: ipa
		  url: http://jenkins.company.com:8080/artifactory/repo-snapshots
		  repositoryId: repo-snapshots
		  opts: -q -B -U -s /home/jenkins/.m2/settings.xml
	  preproduction:
		branch: PRE
		maven:
		  file: build/Application.ipa
		  artifactId: iosapp 
		  groupId: com.company
		  packaging: ipa
		  url: http://jenkins.company.com:8080/artifactory/repo-snapshots
		  repositoryId: repo-snapshots
		  opts: -q -B -U -s /home/jenkins/.m2/settings.xml

	deploy:
	  development:
		branch: DEV
		ansible:
		  inventory: $ANSIBLE_HOME/environments/development
		  playbook: $ANSIBLE_HOME/playbooks/deploy_nativeapps.yml
		  platform: IOS
		  packaging: ipa
		  artifact_group: com.company
		  artifact_id: iosapp
		  version: latest
		script:
		  - perl /home/jenkins/CLI/utils/nativeapps/generate_index.pl -c "/Users/jenkins/.ssh/jenkins.rsa"

