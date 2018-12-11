#!/usr/bin/env python

import os

import citadel.nodes.node
import citadel.tools

class Image(citadel.nodes.node.Base):

    def __init__(self, yml, path):
        super(Image, self).__init__(yml, path)
        docker_exec = citadel.tools.find_executable('docker')
       
        self.parser.is_required('name')
        self.parser.is_required('command')
        self.parser.add_default('source', os.getcwd())
        self.parser.add_default('volume', '/src')
        self.parser.add_default('workspace', '/src')
 
        errors, parsed, ignored = self.parser.validate()

        cmd = ['{binary} run --rm -v "{source}:{volume}" -w "{workspace}" "{name}" {command}'.format(
            binary=docker_exec,
            name=parsed['name'],
            source=parsed['source'],
            volume=parsed['volume'],
            workspace=parsed['workspace'],
            command=parsed['command'],
        )]

        self.output.append(citadel.tools.format_cmd(cmd))
