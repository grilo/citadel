RPMFILE=$(find . -type f -name "{file}" -exec ls -rt {{}} \; | tail -1)
VERSION=$(rpm -qp --queryformat '%{{VERSION}}' "$RPMFILE" | sed 's/[-_]SNAPSHOT//g')
