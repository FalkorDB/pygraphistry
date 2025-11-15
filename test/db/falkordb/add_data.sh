#!/bin/bash
set -ex

FALKORDB_HOST=${FALKORDB_HOST:-localhost}
FALKORDB_PORT=${FALKORDB_PORT:-6379}
FALKORDB_PASSWORD=${FALKORDB_PASSWORD:-test}
FALKORDB_GRAPH=${FALKORDB_GRAPH:-social}

# Use redis-cli to execute Cypher queries via FalkorDB
# FalkorDB uses GRAPH.QUERY command

# Create first node (Person A)
redis-cli -h ${FALKORDB_HOST} -p ${FALKORDB_PORT} -a ${FALKORDB_PASSWORD} \
  GRAPH.QUERY ${FALKORDB_GRAPH} \
  "CREATE (a:Person:A {name: 'AA', title: 'tAA', x: 10, y: 20}) RETURN a"

# Create second node (Person B)
redis-cli -h ${FALKORDB_HOST} -p ${FALKORDB_PORT} -a ${FALKORDB_PASSWORD} \
  GRAPH.QUERY ${FALKORDB_GRAPH} \
  "CREATE (b:Person:B {name: 'BB', title: 'tBB', x: 20, y: 30}) RETURN b"

# Create third node (Person C)
redis-cli -h ${FALKORDB_HOST} -p ${FALKORDB_PORT} -a ${FALKORDB_PASSWORD} \
  GRAPH.QUERY ${FALKORDB_GRAPH} \
  "CREATE (c:Person:C {name: 'CC', title: 'tCC', x: 30, y: 40}) RETURN c"

# Create relationships between nodes
redis-cli -h ${FALKORDB_HOST} -p ${FALKORDB_PORT} -a ${FALKORDB_PASSWORD} \
  GRAPH.QUERY ${FALKORDB_GRAPH} \
  "MATCH (a:Person {name: 'AA'}), (b:Person {name: 'BB'}), (c:Person {name: 'CC'}) \
   CREATE (a)-[:KNOWS]->(c), (b)-[:KNOWS]->(c)"

echo "Test data added to FalkorDB graph '${FALKORDB_GRAPH}'"
