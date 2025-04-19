#!/bin/bash

set -e

cat > docker-compose.yml <<EOF
version: '3.8'
services:
EOF

while read -r version; do
  service_name="py${version//./}"

  cat >> docker-compose.yml <<EOF
  $service_name:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: "$version"
    container_name: test_$service_name

EOF

done < .python-versions
