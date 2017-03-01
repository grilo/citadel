# CITADel

CITADel means "Continuous Integration, Testing, And Delivery".

Make your Jenkins behave like a Travis! (.. or a Circle, or a Codeship, or a
GitLab-CI or something else). It draws inspiration and partially emulates
the behaviour of such tools.

## Documentation
https://citadel.readthedocs.io

## Motivation
https://www.ingtechit.es/joaogrilo/inversion-of-control/

## Usage

Clone it and run it:
```
git clone https://github.com/grilo/citadel.git
python citadel/citadel-generate -f <citadel.yml> | bash
```

It also supports environment variables injection:
```
# Export an environment variable to the whole script
./citadel-generate -e "VARIABLE=value"
```

And since you may want to selectively run specific steps, it supports
conditional execution:
```
# Do NOT generate the shell for deploy and test stages
./citadel-generate -i deploy,test
```
