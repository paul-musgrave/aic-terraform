#!/bin/sh
echo "replayData = "|cat - replay.json > /tmp/out && mv /tmp/out data.js