#!/usr/bin/env python

import re

import citadel.nodes.node
import citadel.tools


class Language(citadel.nodes.node.Base):
    """:synopsis: Sets a required language/runtime for the environment.

    :requirements: None
    :platform: Any

    :param language: The language for the build environment.
    :type language: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        language: java1.8

    This is a makeshift module. Theoretically we'd have the capability to
    build containers or virtual machine images which contain the actual
    environment.

    Since some build environments are often used to build absolutely
    everything, we make an attempt at correctly configuring it by setting
    some environment variables before actually starting the builds themselves

    Supported languages are:

    #. java
    #. npm (javascript)
    #. xcode (objective C/swift)

    The language should be specified with a number. Examples below:

    .. code-block:: yaml
        :linenos:

        language: npm2.6
        language: java1.8
        language: java7
        xcode: 8.1

    Depending on the language choice, the heuristic will be different. For Java,
    the "alternatives" command will be used (incompatible with OSX and Windows).
    For npm, the binary will be looked for in the PATH (which command). For
    Xcode, the "xcode-select" command will be used with the following arguments:

    .. code-block:: bash
        :linenos:

        sudo xcode-select -s /Applications/Xcode%s.app' % (wanted_version)

    .. warning::

        For Xcode, make sure the multiple versions are installed in
        /Applications/Xcode{version}.app. Alternatively, you can just omit the
        tag to use the default (whatever you have installed).
    """

    def __init__(self, yml, path):
        super(Language, self).__init__(yml, path)

        if 'java' in yml:
            version = re.search(r'[0-9\.]+', yml).group(0)
            if '.' in version:
                version = '.'.join(version.split('.', 1)[1:])
            self.output.append(self.get_alternatives('javac', 'java-.*[.-]' + version + '[.-]'))
            self.output.append(r'export JAVA_HOME="$(echo $BINARY | sed "s/\/bin\/javac.*//g")"')
        elif 'xcode' in yml:
            wanted_version = re.match(r'xcode([A-Za-z0-9\.\-]+)', yml).group(1)
            self.output.append('sudo xcode-select -s /Applications/Xcode%s.app' % (wanted_version))

    def get_alternatives(self, binary, wildcard):
        """Best effort at finding installed software without doing a 'find /'."""
        return """
BINARY="%s"
BINLOCATOR="update-alternatives"

if ! which update-alternatives > /dev/null ; then
    BINLOCATOR="/usr/sbin/update-alternatives"
fi

if ! $($BINLOCATOR --list $BINARY > /dev/null 2>&1) ; then
    BINLOCATOR="$BINLOCATOR --display"
else
    BINLOCATOR="$BINLOCATOR --list"
fi

BINARY=$($BINLOCATOR $BINARY | sed 's/ - .*//g' | grep "^/.*%s")""" % (binary, wildcard)
