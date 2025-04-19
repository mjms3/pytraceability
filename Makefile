.PHONY: test generate-compose clean

# Default to running tests for all versions
PYTHON_VERSION ?= all

generate-compose:
	./generate-compose.sh

test: generate-compose
	./run_tests.sh $(PYTHON_VERSION)

clean:
	docker-compose down --rmi local
