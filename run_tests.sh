#!/bin/bash

log_file="test_output.log"
failures=()

echo "=== Test Run Log ===" > "$log_file"

PYTHON_VERSION=${1:-all}

versions=()
while read -r version; do
  versions+=("$version")
done < .python-versions

if [ "$PYTHON_VERSION" != "all" ]; then
  versions=("$PYTHON_VERSION")
fi

for version in "${versions[@]}"; do
  service="py${version//./}"
  echo "=== Running tests in Python $version ==="

  docker compose build "$service" && docker compose run --rm -T "$service" | tee -a "$log_file"
  result=${PIPESTATUS[0]}


  if [ $result -eq 0 ]; then
    echo "✅ Tests passed for Python $version"
  else
    echo "❌ Tests failed for Python $version"
    failures+=("$version")
  fi
done


echo ""
echo "=== Full Test Run Output ==="
cat "$log_file"


if [ ${#failures[@]} -ne 0 ]; then
  echo ""
  echo "=== ❌ Failed Python versions: ${failures[*]} ==="
  exit 1
else
  echo ""
  echo "=== ✅ All tests passed! ==="
fi
