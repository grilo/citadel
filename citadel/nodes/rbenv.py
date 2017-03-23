#!/usr/bin/env python

import logging

import citadel.nodes.node
import citadel.tools


class Rbenv(citadel.nodes.node.Base):
    """:synopsis: Sets up a basic ruby environment.

    :requirements: internet connection, git client, curl
    :platform: Any

    :param ruby: The ruby version to be installed
    :type ruby: optional

    :param cocoapods: The cocoapods to be installed
    :type cocoapods: optional

    **Usage**

    .. code-block:: yaml
        :linenos:

        rbenv:
          ruby: 2.3.0
          cocoapods: 1.1.0

    .. warning::

        If any RVM version is installed, it will get imploded.

    This module will download the contents of the rbenv git repository and/or
    the contents of the CocoaPods git repository. It will also build the
    source version of the provided ruby version if not found already in the
    system, meaning it might take a while to setup the environment.

    Before installing cocoapods, it will make sure any other versions do
    not exist by uninstalling them all.

    After installing cocoapods, it will also run a "pod setup" and
    "pod install" on the current working directory.

    This module also has special behaviour to support older versions of
    CocoaPods (<=0.3.x). This was precisely the rationale for creating
    it since critical issues were found when building multiple projects
    with very different requirements on the same OSX machine (iOS apps).
    """

    def __init__(self, yml, path):
        super(Rbenv, self).__init__(yml, path)

        if 'ruby' in self.yml.keys():
            logging.info('Detected ruby version request: %s', self.yml['ruby'])
            self.output.append(
                citadel.tools.template('rbenv', {
                    'ruby_version': self.yml['ruby']
                })
            )

        if 'cocoapods' in self.yml.keys():
            logging.info('Detected cocoapods version request: %s', self.yml['cocoapods'])
            self.output.append(
                citadel.tools.template('cocoapods', {
                    'cocoapods_version': self.yml['cocoapods']
                })
            )
