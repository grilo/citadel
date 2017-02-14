rm -f api/*
sphinx-apidoc -e -T -M -o api ../citadel
find api -type f -name "*yaml*" -exec rm -f {} \; 
find api -type f ! -name "*node*" -exec rm -f {} \; 
rm api/citadel.nodes.rst
make html
