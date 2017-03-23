if [ -d ppbuddy ] ; then
    rm -fr ppbuddy
fi
git clone https://github.com/grilo/ppbuddy.git
cmd="{command}"
if [[ $ENVIRONMENT =~  PRO ]] ; then
    cmd="$cmd --production"
fi
output=$($cmd)
UUID=$(echo "$output" | head -1 | awk -F@ '{{print $1}}')
PP_NAME=$(echo "$output" | head -1 | awk -F@ '{{print $2}}')
CODE_SIGN_IDENTITY=$(echo "$output" | head -1 | awk -F@ '{{print $3}}')
TEAM_ID=$(echo "$output" | head -1 | awk -F@ '{{print $4}}')
