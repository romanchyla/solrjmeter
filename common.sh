#!/bin/bash

export DURATION=${PERF_DURATION:-150}
export TARGET_URL=${PERF_TARGET_URL:-/solr/collection1}
export COLLECTION=${PERF_COLLECTION:-collection1}
export SERVER=${PERF_SERVER:-localhost}
export PORT=${PERF_PORT:-9983}
