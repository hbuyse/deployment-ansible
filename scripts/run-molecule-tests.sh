#!/usr/bin/env bash
#
# Pre-commit hook: run "molecule test" for every changed role that has a
# molecule/ directory. Roles without tests are silently skipped.

set -euo pipefail

if ! command -v molecule > /dev/null 2>&1; then
    echo "molecule is not installed; skipping Molecule tests (see README.md#testing)." >&2
    exit 0
fi

declare -A roles_to_test=()

for path in "$@"; do
    role="$(printf '%s\n' "${path}" | sed -n 's#^roles/\([^/]*\)/.*#\1#p')"
    [ -n "${role}" ] || continue
    [ -d "roles/${role}/molecule" ] && roles_to_test["${role}"]=1
done

if [ ${#roles_to_test[@]} -eq 0 ]; then
    exit 0
fi

status=0
for role in "${!roles_to_test[@]}"; do
    echo "==> Running Molecule tests for role '${role}'"
    if ! (cd "roles/${role}" && molecule test); then
        status=1
    fi
done

exit "${status}"
