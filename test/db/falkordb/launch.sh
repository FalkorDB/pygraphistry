#!/bin/bash
set -ex

WITH_SUDO=${WITH_SUDO-sudo}

${WITH_SUDO} docker compose -f falkordb.yml down -v || exit 1
${WITH_SUDO} docker compose -f falkordb.yml up -d || exit 1
${WITH_SUDO} ./wait_falkordb.sh
FALKORDB_PORT=6379 ./add_data.sh || exit 1
