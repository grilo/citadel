#!/usr/bin/env python

import logging
import os

import citadel.nodes.node
import citadel.tools


class Rpm(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Rpm, self).__init__(yml, path)

        self.parser.is_required('files')
        self.parser.is_required('buildroot')
        self.parser.add_default('target', ['noarch'])
        self.parser.is_required('Name')
        self.parser.is_required('Version')
        self.parser.add_default('Release', '1')
        self.parser.add_default('Summary', "No summary provided.")
        self.parser.add_default('License', "GPLv3")
        self.parser.add_default('description', "No description provided.")

        errors, parsed, ignored = self.parser.validate()
        self.errors.extend(errors)

        if not isinstance(parsed['files'], list):
            self.errors.append('files must be a list.')
            return

        if not isinstance(parsed['target'], list):
            parsed['target'] = parsed['target'].split()

        for d in ['BUILD', 'RPMS', 'SOURCES', 'SPECS', 'SRPMS']:
            directory = os.path.join(parsed['buildroot'], d)
            self.output.append('mkdir -p "%s"' % (directory))

        file_list = []
        parsed['install'] = ""
        for f in parsed['files']:
            self.output.append('cp -a "%s" "%s/BUILD"\n' % (f, parsed['buildroot']))
            file_list.append('/%s' % (f))
            parsed['install'] += 'cp -a "%s" "\$RPM_BUILD_ROOT/"\n' % (f)

        parsed['path'] = os.path.join(parsed['buildroot'], 'SPECS', 'rpm.spec')

        if len(self.errors) > 0:
           return

        tpl = citadel.tools.template('rpmspec', {
            'buildroot': parsed['buildroot'],
            'Name': parsed['Name'],
            'Version': parsed['Version'],
            'Release': parsed['Release'],
            'Summary': parsed['Summary'],
            'License': parsed['License'],
            'install': parsed['install'],
            'files': '\n'.join(file_list),
            'description': parsed['description'],
        })
        self.output.append('echo "%s" > "%s"' % (tpl, parsed['path']))

        rpmbuild = 'rpmbuild --verbose -bb'
        rpmbuild += ' --define "_topdir %s"' % (parsed['buildroot'])
        rpmbuild += ' --define "_tmppath %{_topdir}/tmp"'
        rpmbuild += ' --target="%s"' % (','.join(parsed['target']))
        rpmbuild += ' "%s/SPECS/rpm.spec"' % (parsed['buildroot'])

        self.output.append(rpmbuild)
