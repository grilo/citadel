#!/usr/bin/env python

import copy


class Options:

    def __init__(self, yml):
        self.yml = copy.deepcopy(yml)
        self.required = []
        self.at_least = []
        self.at_most = []
        self.one_and_all = []
        self.accounted = []

    def add_default(self, key, value):
        if not key in self.yml.keys():
            self.yml[key] = value

    def is_required(self, opt):
        self.required.append(opt)

    def at_least_one(self, opts):
        self.at_least.append(opts)

    def at_most_one(self, opts):
        self.at_most.append(opts)

    def if_one_then_all(self, opts):
        self.one_and_all.append(opts)

    def validate(self):
        errors = []
        ignored = {}

        if not isinstance(self.yml, dict):
            errors.append('Expected a python dict, probably malformed YML syntax.')
            return errors, {}, {}

        for req in self.required:
            self.accounted.append(req)
            if not req in self.yml.keys():
                errors.append('The following field is required: %s' % (req))

        for group in self.at_least:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found == 0:
                errors.append('At least one of the following is mandatory: %s' % (' '.join(group)))

        for group in self.at_most:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found > 1:
                errors.append('At most one of the following values may be specified: %s' % (' '.join(group)))

        for group in self.one_and_all:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found > 0 and found != len(group):
                errors.append('The following values must be specified together: %s' % (' '.join(group)))

        for k, v in self.yml.items():
            if not k in self.accounted:
                ignored[k] = v

        return errors, self.yml, ignored
