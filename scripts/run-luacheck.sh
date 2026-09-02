#!/usr/bin/env bash
#
# Pre-commit hook: run luacheck against the changed Lua files.
#
# The upstream "lunarmodules/luacheck" pre-commit hook builds luacheck via
# luarocks against whatever Lua interpreter "luarocks" auto-detects as the
# system default. On systems whose default Lua is very recent (5.5+),
# luacheck's own bundled sources currently fail to load ("attempt to assign
# to const variable"). Pre-commit's "lua" language has no way to pin an
# older interpreter for a single hook (it only supports the system default),
# so instead we build our own luacheck against Lua 5.4 in a private,
# self-contained tree, cached outside the repo, and call it directly.

set -euo pipefail

TREE="${XDG_CACHE_HOME:-${HOME}/.cache}/deployment-ansible/luarocks-lua5.4"
LUACHECK="${TREE}/bin/luacheck"

if [ ! -x "${LUACHECK}" ]; then
    if ! command -v luarocks > /dev/null 2>&1 || ! command -v lua5.4 > /dev/null 2>&1; then
        echo "luarocks and/or lua5.4 are not installed; skipping luacheck (see README.md)." >&2
        exit 0
    fi

    echo "==> Building luacheck against Lua 5.4 (one-time, cached in ${TREE})"
    luarocks --lua-version=5.4 --tree "${TREE}" install luacheck
fi

exec "${LUACHECK}" "$@"
