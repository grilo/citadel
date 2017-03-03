#!/usr/bin/env python

"""Generic options parser."""

import copy


class Options(object):
    """Enforce a given dictionary's keys complies with a set of rules."""

    def __init__(self, yml):
        self.yml = copy.deepcopy(yml)

        if self.yml is None:
            raise SyntaxError('Parsing error, probably malformed yaml. Check the log for warnings.')

        self.required = []
        self.at_least = []
        self.at_most = []
        self.one_and_all = []
        self.accounted = []

    def add_default(self, key, value):
        """If the key doesn't exist, create it with the value."""
        if not key in self.accounted:
            self.accounted.append(key)
        if not key in self.yml.keys():
            self.yml[key] = value

    def is_required(self, opt):
        """Ensure the key exists."""
        self.required.append(opt)

    def at_least_one(self, opts):
        """At least one of the provided keys."""
        self.at_least.append(opts)

    def at_most_one(self, opts):
        """At most one of the provided keys."""
        self.at_most.append(opts)

    def if_one_then_all(self, opts):
        """If any of the provided keys exist, all must exist."""
        self.one_and_all.append(opts)

    def validate_required(self):
        """Validate all mandatory parameters exist."""
        errors = []
        for req in self.required:
            self.accounted.append(req)
            if not req in self.yml.keys():
                errors.append('The following field is required: %s' % (req))
        return errors

    def validate_at_least(self):
        """Validate at least one of the provided keys exists."""
        errors = []
        for group in self.at_least:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found == 0:
                errors.append('At least one of the following is mandatory: %s' % (' '.join(group)))
        return errors

    def validate_at_most(self):
        """Validate one and only one of the keys exists."""
        errors = []
        for group in self.at_most:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found > 1:
                errors.append('At most one of the following values may be specified: %s' %
                              (' '.join(group)))
        return errors

    def validate_one_and_all(self):
        """Validate that if any of these keys exist, all exist."""
        errors = []
        for group in self.one_and_all:
            self.accounted.extend(group)
            found = 0
            for value in group:
                if value in self.yml:
                    found += 1
            if found > 0 and found != len(group):
                errors.append('The following values must be specified together: %s' %
                              (' '.join(group)))
        return errors


    def validate(self):
        """Validation engine, enforce all of the above rules.

        Returns:
            * errors: a list of errors found (keys which don't comply).
            * yml: a dictionary populated with default values.
            * ignored: keys found that had no rule attached to them.
        """
        errors = []
        ignored = {}

        if not isinstance(self.yml, dict):
            errors.append('Expected a python dict, probably malformed YML syntax.')
            return errors, {}, {}

        errors.extend(self.validate_required())
        errors.extend(self.validate_at_least())
        errors.extend(self.validate_at_most())
        errors.extend(self.validate_one_and_all())

        for key, value in self.yml.items():
            if not key in self.accounted:
                ignored[key] = value

        return errors, self.yml, ignored
