# CITADel

CITADel means "Continuous Integration, Testing, And Delivery".

Initially built to emulate the behaviour of online tools such as TravisCI,
CircleCI and GitLab-CI, also draws inspiration from them.

## Documentation
The project's documentation may be found in: http://citadel.readthedocs.io

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
