#!/bin/sh
set -eu

workspace=${1:-$PWD}
owner="$(id -u):$(id -g)"
for cache in /opt/opam /opt/nuget; do
    if [ "$(stat -c '%u:%g' "$cache")" != "$owner" ]; then
        sudo chown -R "$owner" "$cache"
    fi
done

python3 "$(dirname "$0")/setup.py" "$workspace"
make -C "$workspace" doctor
