#!/bin/bash

echo "Restore Matching Engine"

aws s3 cp \
s3://coinguard-backups/engine/latest.snapshot \
/tmp/

./matching-engine \
--restore /tmp/latest.snapshot

./replay_wal \
--source kafka

echo "Restore completed"