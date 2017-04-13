#!/usr/bin/env python

import citadel.nodes.node
import citadel.tools


class Maven(citadel.nodes.node.Base):
    """:synopsis: Run Maven for either generating or publishing an artifact.

    :requirements: None
    :platform: Any


    The maven module may be used both for building a project and publishing
    an artifact. The publishing means that the files will be uploaded to
    a standard maven repository following all of its conventions.

    Since a maven build may generate multiple artifacts, typically impossible
    to correctly assess without fully running the reactor, it's left to the
    user which ones should actually be published.

    As such, it's discouraged (though in no way forbidden) to use a lifecycle
    such as "clean deploy", thus allowing each artifact published explicitly
    at the publish stage without errors since, in the case of non-snapshot
    repositories, no duplicate versions are allowed.

    **Build**

    :param pom: The pom file to be used.
    :type pom: optional

    :param lifecycle: The lifecycle stages to be run (default: clean assemble).
    :type lifecycle: optional

    :param opts: Additional maven options.
    :type opts: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        build:
          maven:
            lifecycle: clean install

    By default, the pom.xml file that exists in the same directory of the
    citadel.yml file will be invoked. If any other file is meant to be
    executed, the ``pom`` directive should be used.

    Take into account that the normal maven behaviour is look for a settings
    XML file in the $USER directory (/home/user/.m2/settings.xml).

    Since the build typically requires downloading artifacts from remote
    repositories, the settings.xml can be overridden using the ``opts``
    directive:

    .. code-block:: yaml
        :linenos:

        build:
          maven:
            lifecycle: clean install
            pom: anotherpom.xml
            opts: -s special.settings.xml

    Additional options may be passed and will be treated as standard
    options for the maven executable. As such, the following example:

    .. code-block:: yaml
        :linenos:

        build:
          maven:
            lifecycle: clean install
            skipTests: True
            another.option: SomeValue

    Would be translated as:

    .. code-block:: bash
        :linenos:

        mvn -f pom.xml -DskipTests=True -Danother.option=SomeValue


    **Publish**

    :param file: The file to be uploaded.
    :type file: required

    :param artifactId: The artifact's ID to be published with.
    :type artifactId: required

    :param groupId: The artifact's group ID to be published with.
    :type groupId: required

    :param version: The version of the artifact being published.
    :type version: optional

    :param snapshot: Whether the artifact should be published as SNAPSHOT.
    :type snapshot: optional

    :param opts: Additionl options being passed to maven.
    :type opts: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        publish:
          - maven:
              file: target/artifact*.jar
              artifactId: myArtifact
              groupId: com.company.project
          - maven:
              file: target/anotherArtifact*.jar
              artifactId: SpecialProject
              groupId: com.company.project

    The *deploy* option from maven should **NOT** be confused with the actual
    deployment procedure of citadel. Within the maven context, *deploy*
    typically (may be overriden) means uploading the artifacts to a
    maven-compliant repository.

    Using a standard configuration, *deploy* in maven is the direct equivalent
    to citadel's ``publish``.

    Using maven within the publish directive provides the option of segregating
    the build and publish stages. The reasoning behind this separation is that
    it may be useful for Continuous Integration environments to run the builds
    without side effects (in this case, uploading artifacts).

    Underneath, this uses maven's deploy:deploy (<plugin>:<goal>). The maven
    executable being used is whatever comes up by running the *which* command.

    If no version is specified, citadel will attempt to induce the artifact's
    version. The heuristic is based on whatever the user sets in the file
    directive and a few pre-established conventions. Currently, citadel
    supports reading versions from the following types:

    * apk (Android)
    * jar/war/ear (Java Archive)
    * car (Carbon Archive)
    * ipa (iOS)
    * rpm (RedHat Package Manager)

    If any other file extension is used, citadel will abort stating it's unable
    to recognize the file's format (contributions are welcome!).

    The recommended behaviour is to let citadel induce the artifact's version,
    thus avoiding multiple files being changed whenever your application's
    versioning changes.

    If multiple artifacts are to be deployed, a yaml list should be
    constructed instead of the plain key:value map.

    Any unrecognized options will be translated into ``-Doption=value``.

    As such, the following:

    .. code-block:: yaml
        :linenos:

        publish:
          maven:
            file: target/artifact.*.jar
            artifactId: myArtifact
            groupId: com.company.project
            snapshot: True
            opts: special.settings.xml

    Would get translated as:

    .. code-block:: bash
        :linenos:

        FILE=$(find target -type f -print | grep -E "target/artifact.*.jar")
        VERSION=$(unzip -p '$FILE' \
            '*com.company.project*/*myArtifact*/pom.properties' \
            | grep version \
            | awk -F= '{print $2}')
        mvn deploy:deploy-file \\
            -Dfile="$FILE-SNAPSHOT" \\ # Snapshot == True adds the -SNAPSHOT suffix
            -Dversion="$VERSION" \\
            -DartifactId="myArtifact" \\
            -DgroupId="com.company.project" \\
            -s special.settings.xml -V -B -U

    """


    def __init__(self, yml, path):
        super(Maven, self).__init__(yml, path)

        # Always display maven's version
        mvn_exec = citadel.tools.find_executable('mvn') + ' -V -B'

        if 'build' in path:

            self.parser.add_default('pom', 'pom.xml')
            self.parser.add_default('lifecycle', 'clean install')
            self.parser.add_default('opts', '')
            errors, parsed, ignored = self.parser.validate()

            cmd = ['%s -f "%s" %s %s' %
                   (mvn_exec, parsed['pom'], parsed['lifecycle'], parsed['opts'])]
            for key, value in ignored.items():
                cmd.append('-D%s=%s' % (key, value))
            self.output.append(citadel.tools.format_cmd(cmd))

        elif 'publish' in path:

            self.parser.add_default('opts', '')
            self.parser.is_required('file')
            self.parser.is_required('url')
            self.parser.is_required('repositoryId')

            if 'pomFile' in yml.keys():
                self.parser.is_required('pomFile')
                errors, parsed, ignored = self.parser.validate()
                self.errors.extend(errors)
                self.output.append(citadel.tools.find_file(parsed['pomFile'], 'POMFILE'))
                parsed['pomFile'] = '$POMFILE'
            else:
                self.parser.add_default('version', '${VERSION}')
                self.parser.add_default('snapshot', False)
                self.parser.is_required('artifactId')
                self.parser.is_required('groupId')

                errors, parsed, ignored = self.parser.validate()
                self.errors.extend(errors)

                if parsed['file'] and parsed['version'] == '${VERSION}':

                    artifact = parsed['file']
                    version = ''

                    if artifact.endswith('.apk'):
                        version = self.read_apk_version(artifact)
                    elif artifact.endswith('.jar') or \
                            artifact.endswith('.war') or \
                            artifact.endswith('.ear'):
                        version = self.read_jar_version(artifact,
                                                        parsed['groupId'],
                                                        parsed['artifactId'])
                    elif artifact.endswith('.ipa'):
                        version = self.read_ipa_version()
                    elif artifact.endswith('.rpm'):
                        version = self.read_rpm_version(artifact)
                    elif artifact.endswith('.car'):
                        version = self.read_car_version(artifact)
                    else:
                        self.add_error('Unable to automatically induce version for: %s' %
                                       (parsed['file']))

                    self.output.append(version)

                if parsed['snapshot'] and not '-SNAPSHOT' in parsed['version']:
                    parsed['version'] += '-SNAPSHOT'


            self.output.append(citadel.tools.find_file(parsed['file']))
            parsed['file'] = "$FILE"

            cmd = ['%s deploy:deploy-file %s' % (mvn_exec, parsed['opts'])]

            del parsed['opts']
            for key, value in parsed.items():
                cmd.append('-D%s="%s"' % (key, value))
            for key, value in ignored.items():
                cmd.append('-D%s="%s"' % (key, value))

            self.output.append(citadel.tools.format_cmd(cmd))

    def read_apk_version(self, artifact):
        """Read version from an APK file."""
        return citadel.tools.template('maven_readapk', { 'artifact': artifact })

    def read_jar_version(self, artifact, group_id, artifact_id):
        """Read version from a JAR file."""
        return citadel.tools.template('maven_readjar', {
            'file': artifact,
            'group_id': group_id,
            'artifact_id': artifact_id,
        })

    def read_car_version(self, artifact):
        """Read version from a CAR file."""
        return citadel.tools.template('maven_readcar', {'file': artifact})

    def read_ipa_version(self):
        """Thanks Steve."""
        return citadel.tools.template('maven_readipa')

    def read_rpm_version(self, artifact):
        """Read version from an RPM file."""
        return citadel.tools.template('read_rpm', {'file': artifact})
