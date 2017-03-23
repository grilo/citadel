export RBENV_VERSION="{ruby_version}"
export RBENV_DIR=$HOME/.rbenv
export RUBY_CONFIGURE_OPTS="--disable-install-doc"
if which rvm ; then
    echo "yes" | rvm implode
fi

if [ ! -d "$RBENV_DIR" ] ; then
    git clone https://github.com/rbenv/rbenv.git "$RBENV_DIR"
else
    cd "$RBENV_DIR"
    git pull
    cd -
fi

if [ ! -d "$RBENV_DIR/plugins/ruby-build" ] ; then
    git clone https://github.com/rbenv/ruby-build.git ~/.rbenv/plugins/ruby-build
else
    cd "$RBENV_DIR/plugins/ruby-build"
    git pull
    cd -
fi

export PATH="$HOME/.rbenv/bin:$PATH"
eval "$(rbenv init -)"

if ! rbenv versions | grep "$RBENV_VERSION" ; then
    echo "This might take a few minutes..."
    rbenv install $RBENV_VERSION
fi
