NPM_VERSION="{npm_version}"
if ! which npm > /dev/null ; then
    echo "At least one npm version must be installed to boostrap any further npm installations."
    exit 1
fi
npm install npm@$NPM_VERSION
export PATH="node_modules/.bin:$PATH"
echo "NPM version: $(npm --version)" 
