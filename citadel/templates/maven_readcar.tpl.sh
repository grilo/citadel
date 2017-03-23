VERSION=$(unzip -p '{file}' 'artifacts.xml' \
    | grep 'artifact name' \
    | awk -F\\\" '{print $4}')
