VERSION=$(unzip -p '{file}' '*{group_id}*/*{artifact_id}*/pom.properties' \
    | grep version \
    | awk -F= '{print $2}')

