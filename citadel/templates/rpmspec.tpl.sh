Name: {Name}
Version: {Version}
Release: {Release}
Summary: {Summary}
License: {License}

%description
{description}

%install
if [ ! -d \$RPM_BUILD_ROOT ] ; then
    mkdir -p \$RPM_BUILD_ROOT
fi
{install}

%files
{files}
