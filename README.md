# CITADel

CITADel means "Continuous Integration, Testing, And Delivery".

Initially built to emulate the behaviour of online tools such as TravisCI,
CircleCI and GitLab-CI, also draws inspiration from them.

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
# Generate only the deploy and test stages
./citadel-generate -i deploy,test
```

## Motivation

Although the cloud offerings are nothing short of fantastic, in the
corporate environment they're often not a choice due to internal budget
restrictions or security concerns. The "jenkinsfile" concept is sound,
but it's attached to a specific tool (Jenkins) and lacks any meaningful
documentation to actually be of value.

The goal is to have a file at the root of your project which describes the
general lifecycle of your product (build, publish, testing and deployment).
The YML description gets translated into a shell (bash) script, ready to
be executed.

It's a complement to the tools usually used to build projects (such as maven,
gradle, npm). Those tools usually excel at generating artifacts (condensed
in the build and publish phase of CITADel), but they aren't very friendly
when it comes to deploying and testing the actuall product.

## Goals

Should be easy to use (creating the yml description) and easy to extend
(adding new modules).

It should also generate a shell script, independent of the system where
it was initially executed. This shell script is meant to be discarded
but it may also be versioned to ensure build reproduceability.
