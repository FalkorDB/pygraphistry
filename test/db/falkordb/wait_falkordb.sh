#!/bin/bash

export CONTAINER=${CONTAINER:-falkordb-test}
export FALKORDB_PASSWORD=${FALKORDB_PASSWORD:-test}
export FALKORDB_PORT=${FALKORDB_PORT:-6379}

echo "wait for FalkorDB to respond at port ${FALKORDB_PORT}"

# Wait for FalkorDB to be ready by checking Redis connection
docker exec -t ${CONTAINER} \
  bash -c "until redis-cli -a ${FALKORDB_PASSWORD} ping | grep -q PONG; do echo 'Waiting for FalkorDB...'; sleep 1; done"

echo 'FalkorDB online!'

exit 0
