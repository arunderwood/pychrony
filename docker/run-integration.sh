#!/bin/sh
# Start chronyd, wait until it is ready, then run pytest inside the test image.
# Shared by ci.yml and release.yml. Arguments are passed to pytest; with none,
# the whole suite runs.
set -eu

chronyd

# chronyd answers commands before it has resolved its server name, and
# the source list changes as the name resolves. Tests that
# walk the source list race that growth, so wait until no source has an
# unresolved address. chronyc also fails until the command socket is up.
# The 40s limit covers one failed DNS lookup: chronyd retries unresolved
# names 28s after its first attempt.
i=0
until chronyc -n activity 2>/dev/null | grep -q "^0 sources with unknown address"; do
  i=$((i + 1))
  if [ "$i" -ge 80 ]; then
    echo "chronyd sources not resolved after 40s"
    chronyc -n activity
    exit 1
  fi
  sleep 0.5
done
echo "chronyd sources resolved after $i polls"

if [ "$#" -eq 0 ]; then
  set -- tests/ -v --tb=short
fi
exec pytest "$@"
