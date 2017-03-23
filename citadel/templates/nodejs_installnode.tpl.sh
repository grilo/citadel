{downloader}
NODE_VERSION="{node_version}"
[ ! -f "node-${NODE_VERSION}-linux-x64.tar.gz" ] || rm -f node-${NODE_VERSION}-linux-x64.tar.gz
${DOWNLOADER} https://nodejs.org/download/release/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.gz
[ ! -d "node-${NODE_VERSION}-linux-x64.tar.gz" ] || rm -fr node-${NODE_VERSION}-linux-x64.tar.gz
tar -xzf node-${NODE_VERSION}-linux-x64.tar.gz
rm -f node-${NODE_VERSION}-linux-x64.tar.gz
export PATH="node-${NODE_VERSION}-linux-x64/bin:$PATH"
echo "Node version: $(node --version)"
