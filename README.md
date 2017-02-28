# CITADel

CITADel means "Continuous Integration, Testing, And Delivery".

Draws inspiration from, and emulates the behaviour of, tools such as TravisCI,
CircleCI and GitLab-CI.

## Documentation
https://citadel.readthedocs.io

## Motivation
https://www.ingtechit.es/joaogrilo/inversion-of-control/

## Usage

There's packaging basis already in the repository, but the most
straightforward way currently is:
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
