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

## Jenkinsfile

CITADel now supports "Pipeline script" jobs in jenkins. This change is purely cosmetic, but greatly enhaces visual feedback.

To enable this:
  1. Create a new job in jenkins of type "Pipeline".
  2. Ensure that "Pipeline" is set to "Pipeline script".
  3. Fill in the contents which the script below (example):
``` groovy
    node {
        dir('/home/user/git/some_project') {
            sh 'python citadel-generate -o jenkins > jenkinsfile'
            load('jenkinsfile')
        }
    }() // Closure important!
```
You may want to fill in some stuff before/after (such as checking out from your SCM). The result should be similar to the example found [here](https://www.cloudbees.com/sites/default/files/blog/pipeline-vis.png). The actual name of the steps will be mapped directly to the contents of the citadel.yml file.
