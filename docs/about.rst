=====
About
=====

CITADel (Continuous Integration Testing And DELivery) is heavily inspired by
tools such as `<https://travis-ci.org>`_, `<https://circleci.com>`_ and the likes. The goals
is to provide autonomy and allow the developer to decouple his/her project
from the standard lifecycle tools such as Jenkins.

By describing the build/deployment using a yaml file (the complexity will vary
depending on the requirements), you can now run your application's lifecycle
in any environment (currently it must support bash). This means that any
Jenkins job you configure simply needs to invoke CITADel and the rest will be
taken care of, effectively transforming your own CI solution into something
similar to other offerings from the cloud.

The citadel.yml file (by default, it can be anything else) describes your
project's lifecycle. It's not an executor/runner by itself, it simply
translates whatever there is in the yml file into standard bash which can then
be executed at your discretion.
