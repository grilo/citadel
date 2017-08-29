rm -f api/*
sphinx-apidoc -e -T -M -o api ../citadel
find api -type f -name "*yaml*" -exec rm -f {} \; 
find api -type f ! -name "*node*" -exec rm -f {} \; 
find api -type f -name "*.rst" -exec sed -i '/:show-inheritance:/d' {} \;
find api -type f -name "*.rst" -exec sed -i 's/:undoc-members:/:no-undoc-members:/g' {} \;
rm api/citadel.nodes.node.rst
rm api/citadel.nodes.rst
make html
