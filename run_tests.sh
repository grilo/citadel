#!/usr/bin/env bash

set -eu
set -o pipefail

if ! output=$(pip install nose2 > /dev/null 2>&1) ; then
    echo "$output"
    exit 1
fi
#nose2 --log-level DEBUG
nose2
